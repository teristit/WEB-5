from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.index, name='index'),
    path('play/', views.game_view, name='game'),
    path('play/<int:level_id>/', views.game_view, name='game_level'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('achievements/', views.achievements_view, name='achievements'),
    
    # API endpoints
    path('api/start/', views.start_game, name='api_start_game'),
    path('api/update/', views.update_game_state, name='api_update_game'),
    path('api/end/', views.end_game, name='api_end_game'),
    path('api/login/', views.login_user, name='api_login'),
    path('api/register/', views.register_user, name='api_register'),
    path('api/logout/', views.logout_user, name='api_logout'),
]