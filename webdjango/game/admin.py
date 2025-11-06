from django.contrib import admin
from .models import GameLevel, Player, GameSession, Achievement, PlayerAchievement, GameSprite


@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['name']
    ordering = ['difficulty', 'name']


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'best_score', 'current_level', 'games_played', 'created_at']
    list_filter = ['current_level', 'created_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['-best_score']
    readonly_fields = ['created_at']


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['player', 'level', 'score', 'completed', 'start_time']
    list_filter = ['completed', 'level', 'start_time']
    search_fields = ['player__user__username', 'level__name']
    ordering = ['-start_time']
    readonly_fields = ['start_time']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'achievement_type', 'requirement', 'points']
    list_filter = ['achievement_type']
    search_fields = ['name', 'description']


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ['player', 'achievement', 'earned_at']
    list_filter = ['achievement', 'earned_at']
    search_fields = ['player__user__username', 'achievement__name']
    ordering = ['-earned_at']


@admin.register(GameSprite)
class GameSpriteAdmin(admin.ModelAdmin):
    list_display = ['name', 'sprite_type', 'width', 'height', 'animation_frames']
    list_filter = ['sprite_type']
    search_fields = ['name']