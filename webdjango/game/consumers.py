import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Player, GameSession, GameLevel


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        # Присоединяемся к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'player_move':
            # Обрабатываем движение игрока
            await self.handle_player_move(text_data_json)
        elif message_type == 'game_state':
            # Обрабатываем обновление состояния игры
            await self.handle_game_state(text_data_json)
        elif message_type == 'chat_message':
            # Обрабатываем чат сообщения
            await self.handle_chat_message(text_data_json)

    async def handle_player_move(self, data):
        """Обработка движения игрока в мультиплеере"""
        # Отправляем обновление всем игрокам в комнате
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_update',
                'player_id': data.get('player_id'),
                'position': data.get('position'),
                'animation': data.get('animation'),
            }
        )

    async def handle_game_state(self, data):
        """Обработка обновления состояния игры"""
        # Сохраняем состояние игры в базу данных
        if self.scope['user'].is_authenticated:
            await self.save_game_state(data)

        # Отправляем обновление всем игрокам
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_state': data.get('game_state'),
                'timestamp': data.get('timestamp'),
            }
        )

    async def handle_chat_message(self, data):
        """Обработка чат сообщений"""
        message = data['message']
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Аноним'

        # Отправляем сообщение всем в комнате
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': data.get('timestamp'),
            }
        )

    async def player_update(self, event):
        """Отправка обновления позиции игрока"""
        await self.send(text_data=json.dumps({
            'type': 'player_update',
            'player_id': event['player_id'],
            'position': event['position'],
            'animation': event['animation'],
        }))

    async def game_update(self, event):
        """Отправка обновления состояния игры"""
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'game_state': event['game_state'],
            'timestamp': event['timestamp'],
        }))

    async def chat_message(self, event):
        """Отправка чат сообщения"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def save_game_state(self, data):
        """Сохранение состояния игры в базу данных"""
        try:
            user = self.scope['user']
            player = Player.objects.get(user=user)
            
            # Находим активную сессию или создаем новую
            session = GameSession.objects.filter(
                player=player,
                completed=False
            ).first()
            
            if session:
                session.game_data.update(data.get('game_state', {}))
                session.score = data.get('game_state', {}).get('score', 0)
                session.save()
                
        except (User.DoesNotExist, Player.DoesNotExist):
            pass


class LobbyConsumer(AsyncWebsocketConsumer):
    """WebSocket консьюмер для лобби игры"""
    
    async def connect(self):
        self.room_group_name = 'game_lobby'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Отправляем список активных игр
        await self.send_active_games()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'create_room':
            await self.create_game_room(text_data_json)
        elif message_type == 'join_room':
            await self.join_game_room(text_data_json)
        elif message_type == 'get_rooms':
            await self.send_active_games()

    async def create_game_room(self, data):
        """Создание новой игровой комнаты"""
        room_name = data.get('room_name')
        level_id = data.get('level_id', 1)
        max_players = data.get('max_players', 2)
        
        # Уведомляем всех в лобби о новой комнате
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_created',
                'room_name': room_name,
                'level_id': level_id,
                'max_players': max_players,
                'creator': self.scope['user'].username if self.scope['user'].is_authenticated else 'Аноним'
            }
        )

    async def join_game_room(self, data):
        """Присоединение к игровой комнате"""
        room_name = data.get('room_name')
        
        # Уведомляем о присоединении к комнате
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'room_name': room_name,
                'player': self.scope['user'].username if self.scope['user'].is_authenticated else 'Аноним'
            }
        )

    async def send_active_games(self):
        """Отправка списка активных игр"""
        # В реальном приложении здесь бы был запрос к базе данных
        active_games = [
            {
                'room_name': 'Комната 1',
                'level': 'Уровень 1',
                'players': 1,
                'max_players': 2
            },
            {
                'room_name': 'Комната 2',
                'level': 'Уровень 2',
                'players': 2,
                'max_players': 4
            }
        ]
        
        await self.send(text_data=json.dumps({
            'type': 'active_games',
            'games': active_games
        }))

    async def room_created(self, event):
        """Уведомление о создании комнаты"""
        await self.send(text_data=json.dumps({
            'type': 'room_created',
            'room_name': event['room_name'],
            'level_id': event['level_id'],
            'max_players': event['max_players'],
            'creator': event['creator']
        }))

    async def player_joined(self, event):
        """Уведомление о присоединении игрока"""
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'room_name': event['room_name'],
            'player': event['player']
        }))