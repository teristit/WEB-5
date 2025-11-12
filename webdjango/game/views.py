from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from pprint import pprint

from .models import GameLevel, Player, GameSession, Achievement, PlayerAchievement


def index(request):
    """Главная страница игры"""
    levels = GameLevel.objects.all().order_by('difficulty')
    leaderboard = Player.objects.all()[:10]
    
    context = {
        'levels': levels,
        'leaderboard': leaderboard,
    }
    return render(request, 'game/index.html', context)


def game_view(request, level_id=1):
    """Страница игры"""
    level = get_object_or_404(GameLevel, id=level_id)
    pprint(f"Loading level {level_id}: {level.level_data}")  # Для отладкиs
    # Получаем или создаем профиль игрока
    player = None
    if request.user.is_authenticated:
        player, created = Player.objects.get_or_create(user=request.user)
    
    # ИСПРАВЛЕНИЕ: Сериализуем level_map в JSON
    level_map = level.get_level_map()
    pprint(f"Level map for level {level_id}: {level_map}")  # Для отладки
    level_map_json = json.dumps(level_map, ensure_ascii=False)
    
    context = {
        'level': level,
        'player': player,
        'level_map_json': level_map_json,  # ← JSON-строка вместо объекта
    }
    return render(request, 'game/game.html', context)


# ... остальные функции без изменений ...

@csrf_exempt
@require_http_methods(["POST"])
def start_game(request):
    """API для начала новой игры"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)
    
    data = json.loads(request.body)
    level_id = data.get('level_id', 1)
    
    level = get_object_or_404(GameLevel, id=level_id)
    player, created = Player.objects.get_or_create(user=request.user)
    
    # Создаем новую игровую сессию
    session = GameSession.objects.create(
        player=player,
        level=level,
        game_data={'started': True}
    )
    
    return JsonResponse({
        'session_id': session.id,
        'level_data': level.get_level_map(),
        'player_data': {
            'id': player.id,
            'username': player.user.username,
            'current_level': player.current_level,
            'best_score': player.best_score,
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def update_game_state(request):
    """API для обновления состояния игры"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)
    
    data = json.loads(request.body)
    session_id = data.get('session_id')
    game_state = data.get('game_state', {})
    
    session = get_object_or_404(GameSession, id=session_id, player__user=request.user)
    
    # Обновляем данные сессии
    session.game_data.update(game_state)
    session.score = game_state.get('score', 0)
    session.save()
    
    return JsonResponse({'status': 'updated'})


@csrf_exempt
@require_http_methods(["POST"])
def end_game(request):
    """API для завершения игры"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)
    
    data = json.loads(request.body)
    session_id = data.get('session_id')
    final_score = data.get('score', 0)
    completed = data.get('completed', False)
    
    session = get_object_or_404(GameSession, id=session_id, player__user=request.user)
    player = session.player
    
    # Завершаем сессию
    session.score = final_score
    session.completed = completed
    session.end_time = timezone.now()
    session.save()
    
    # Обновляем статистику игрока
    player.games_played += 1
    player.total_score += final_score
    if final_score > player.best_score:
        player.best_score = final_score
    
    if completed and session.level.difficulty >= player.current_level:
        player.current_level = session.level.difficulty + 1
    
    player.save()
    
    # Проверяем достижения
    check_achievements(player, session)
    
    return JsonResponse({
        'status': 'completed',
        'player_stats': {
            'total_score': player.total_score,
            'best_score': player.best_score,
            'games_played': player.games_played,
            'current_level': player.current_level,
        }
    })


def check_achievements(player, session):
    """Проверка и выдача достижений"""
    achievements = Achievement.objects.all()
    
    for achievement in achievements:
        # Проверяем, есть ли уже это достижение у игрока
        if PlayerAchievement.objects.filter(player=player, achievement=achievement).exists():
            continue
        
        earned = False
        
        if achievement.achievement_type == 'score':
            if player.best_score >= achievement.requirement:
                earned = True
        elif achievement.achievement_type == 'level':
            if player.current_level >= achievement.requirement:
                earned = True
        elif achievement.achievement_type == 'time':
            # Проверяем время прохождения уровня
            if session.end_time and session.start_time:
                duration = (session.end_time - session.start_time).total_seconds()
                if duration <= achievement.requirement:
                    earned = True
        
        if earned:
            PlayerAchievement.objects.create(player=player, achievement=achievement)


def leaderboard(request):
    """Страница таблицы лидеров"""
    top_players = Player.objects.all()[:50]
    
    context = {
        'players': top_players,
    }
    return render(request, 'game/leaderboard.html', context)


def achievements_view(request):
    """Страница достижений"""
    all_achievements = Achievement.objects.all()
    player_achievements = []
    
    if request.user.is_authenticated:
        try:
            player = Player.objects.get(user=request.user)
            player_achievements = PlayerAchievement.objects.filter(player=player).values_list('achievement_id', flat=True)
        except Player.DoesNotExist:
            pass
    
    context = {
        'achievements': all_achievements,
        'player_achievements': player_achievements,
    }
    return render(request, 'game/achievements.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    """API для регистрации нового пользователя"""
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Пользователь уже существует'}, status=400)
    
    user = User.objects.create_user(username=username, password=password, email=email)
    Player.objects.create(user=user)
    
    return JsonResponse({'status': 'created', 'username': username})


@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    """API для входа пользователя"""
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        player, created = Player.objects.get_or_create(user=user)
        return JsonResponse({
            'status': 'logged_in',
            'username': username,
            'player_id': player.id
        })
    else:
        return JsonResponse({'error': 'Неверные данные'}, status=401)


def logout_user(request):
    """Выход пользователя"""
    logout(request)
    return JsonResponse({'status': 'logged_out'})
