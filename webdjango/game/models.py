from django.db import models
from django.contrib.auth.models import User
import json


class GameLevel(models.Model):
    """Модель для хранения уровней игры"""
    name = models.CharField(max_length=100, verbose_name="Название уровня")
    level_data = models.TextField(verbose_name="Данные уровня")
    difficulty = models.IntegerField(default=1, verbose_name="Сложность")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Уровень игры"
        verbose_name_plural = "Уровни игры"
        ordering = ['difficulty', 'name']
    
    def __str__(self):
        return f"{self.name} (сложность: {self.difficulty})"
    
    def get_level_map(self):
        """Возвращает уровень как список списков"""
        try:
            return json.loads(self.level_data)
        except json.JSONDecodeError:
            # Если данные в текстовом формате (как в оригинале)
            lines = self.level_data.strip().split('\n')
            return [list(line) for line in lines]


class Player(models.Model):
    """Модель игрока"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    total_score = models.IntegerField(default=0, verbose_name="Общий счет")
    games_played = models.IntegerField(default=0, verbose_name="Игр сыграно")
    best_score = models.IntegerField(default=0, verbose_name="Лучший результат")
    current_level = models.IntegerField(default=1, verbose_name="Текущий уровень")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
        ordering = ['-best_score']
    
    def __str__(self):
        return f"{self.user.username} - {self.best_score} очков"


class GameSession(models.Model):
    """Модель игровой сессии"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sessions')
    level = models.ForeignKey(GameLevel, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, verbose_name="Очки")
    completed = models.BooleanField(default=False, verbose_name="Завершена")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    game_data = models.JSONField(default=dict, verbose_name="Данные игры")
    
    class Meta:
        verbose_name = "Игровая сессия"
        verbose_name_plural = "Игровые сессии"
        ordering = ['-start_time']
    
    def __str__(self):
        status = "Завершена" if self.completed else "В процессе"
        return f"{self.player.user.username} - {self.level.name} ({status})"


class Achievement(models.Model):
    """Модель достижений"""
    ACHIEVEMENT_TYPES = [
        ('score', 'Очки'),
        ('level', 'Уровень'),
        ('time', 'Время'),
        ('special', 'Особое'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES, default='score')
    requirement = models.IntegerField(verbose_name="Требование")
    icon = models.CharField(max_length=50, default='🏆', verbose_name="Иконка")
    points = models.IntegerField(default=10, verbose_name="Очки за достижение")
    
    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"
    
    def __str__(self):
        return self.name


class PlayerAchievement(models.Model):
    """Связь игрока с достижениями"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Достижение игрока"
        verbose_name_plural = "Достижения игроков"
        unique_together = ['player', 'achievement']
    
    def __str__(self):
        return f"{self.player.user.username} - {self.achievement.name}"


class GameSprite(models.Model):
    """Модель для хранения спрайтов игры"""
    SPRITE_TYPES = [
        ('player', 'Игрок'),
        ('enemy', 'Враг'),
        ('platform', 'Платформа'),
        ('item', 'Предмет'),
        ('background', 'Фон'),
        ('effect', 'Эффект'),
    ]
    
    # Определяем доступные состояния для каждого типа спрайта
    ANIMATION_STATES = {
        'player': [
            'IDLE_RIGHT', 'IDLE_LEFT', 'WALK_RIGHT', 'WALK_LEFT',
            'RUN_RIGHT', 'RUN_LEFT', 'JUMP_RIGHT', 'JUMP_LEFT',
            'FALL_RIGHT', 'FALL_LEFT', 'CROUCH_RIGHT', 'CROUCH_LEFT',
            'ATTACK_RIGHT', 'ATTACK_LEFT', 'HURT_RIGHT', 'HURT_LEFT', 'DEATH'
        ],
        'enemy': [
            'IDLE_RIGHT', 'IDLE_LEFT', 'PATROL_RIGHT', 'PATROL_LEFT',
            'CHASE_RIGHT', 'CHASE_LEFT', 'ATTACK_RIGHT', 'ATTACK_LEFT',
            'HURT', 'DEATH'
        ],
        'platform': ['STATIC', 'BREAKING', 'BROKEN', 'MOVING'],
        'item': ['IDLE', 'COLLECTED', 'SHINE'],
        'background': ['LAYER_1', 'LAYER_2', 'LAYER_3', 'SKY'],
        'effect': ['EXPLOSION', 'SMOKE', 'SPARKLE', 'DUST', 'SPLASH']
    }
    
    name = models.CharField(max_length=100, verbose_name="Название")
    sprite_type = models.CharField(max_length=20, choices=SPRITE_TYPES)
    animation_paths = models.JSONField(
        default=dict, 
        verbose_name="Пути к анимациям",
        blank=True
    )
    width = models.IntegerField(default=50, verbose_name="Ширина")
    height = models.IntegerField(default=50, verbose_name="Высота")
    animation_frames = models.IntegerField(default=1, verbose_name="Кадры анимации")
    
    class Meta:
        verbose_name = "Спрайт"
        verbose_name_plural = "Спрайты"
    
    def __str__(self):
        return f"{self.name} ({self.get_sprite_type_display()})"
    
    def get_available_states(self):
        """Получить доступные состояния для данного типа спрайта"""
        return self.ANIMATION_STATES.get(self.sprite_type, [])
    
    def get_animation_path(self, animation_state):
        """Получить путь к анимации по состоянию"""
        return self.animation_paths.get(animation_state, None)


class SpriteAnimation(models.Model):
    """Модель для хранения отдельных анимаций спрайта"""
    sprite = models.ForeignKey(
        GameSprite, 
        on_delete=models.CASCADE, 
        related_name='animations',
        verbose_name="Спрайт"
    )
    animation_state = models.CharField(
        max_length=50, 
        verbose_name="Состояние анимации"
    )
    image = models.ImageField(
        upload_to='sprites/animations/', 
        verbose_name="Изображение анимации"
    )
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        verbose_name = "Анимация спрайта"
        verbose_name_plural = "Анимации спрайтов"
        ordering = ['sprite', 'animation_state', 'order']
        unique_together = ['sprite', 'animation_state']
    
    def __str__(self):
        return f"{self.sprite.name} - {self.animation_state}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Автоматически обновляем JSON в родительском спрайте
        self.sprite.animation_paths[self.animation_state] = self.image.url
        self.sprite.save()