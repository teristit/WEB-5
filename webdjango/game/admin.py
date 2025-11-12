from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import GameLevel, Player, GameSession, Achievement, PlayerAchievement, GameSprite, SpriteAnimation


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


#@admin.register(GameSprite)
#class GameSpriteAdmin(admin.ModelAdmin):
#    list_display = ['name', 'sprite_type', 'width', 'height', 'animation_frames']
#    list_filter = ['sprite_type']
#    search_fields = ['name']


class SpriteAnimationInline(admin.TabularInline):
    model = SpriteAnimation
    extra = 1
    fields = ['animation_state', 'image', 'order', 'preview']
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.image.url
            )
        return "Нет изображения"
    preview.short_description = "Предпросмотр"
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "animation_state":
            # Получаем родительский объект из запроса
            parent_obj_id = request.resolver_match.kwargs.get('object_id')
            if parent_obj_id:
                try:
                    sprite = GameSprite.objects.get(pk=parent_obj_id)
                    # Ограничиваем выбор состояний доступными для данного типа
                    kwargs["choices"] = [
                        (state, state) for state in sprite.get_available_states()
                    ]
                except GameSprite.DoesNotExist:
                    pass
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class GameSpriteAdminForm(forms.ModelForm):
    """Форма для упрощенного создания спрайта"""
    
    # Динамические поля для каждого состояния будут добавляться в __init__
    
    class Meta:
        model = GameSprite
        fields = '__all__'
        widgets = {
            'animation_paths': forms.HiddenInput()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если редактируем существующий объект
        if self.instance and self.instance.pk:
            sprite_type = self.instance.sprite_type
            available_states = GameSprite.ANIMATION_STATES.get(sprite_type, [])
            
            # Добавляем поля для загрузки изображений
            for state in available_states:
                field_name = f'animation_{state.lower()}'
                self.fields[field_name] = forms.ImageField(
                    required=False,
                    label=f"{state}",
                    help_text=f"Загрузите изображение для состояния {state}"
                )
                
                # Если уже есть изображение, показываем его
                existing_path = self.instance.animation_paths.get(state)
                if existing_path:
                    self.fields[field_name].help_text = format_html(
                        '{}<br><img src="{}" style="max-width: 150px; margin-top: 10px;" />',
                        self.fields[field_name].help_text,
                        existing_path
                    )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Обрабатываем загруженные изображения
        sprite_type = instance.sprite_type
        available_states = GameSprite.ANIMATION_STATES.get(sprite_type, [])
        
        for state in available_states:
            field_name = f'animation_{state.lower()}'
            if field_name in self.cleaned_data and self.cleaned_data[field_name]:
                # Сохраняем изображение через связанную модель
                image_file = self.cleaned_data[field_name]
                
                # Создаем или обновляем анимацию
                animation, created = SpriteAnimation.objects.update_or_create(
                    sprite=instance,
                    animation_state=state,
                    defaults={'image': image_file}
                )
        
        if commit:
            instance.save()
        
        return instance


@admin.register(GameSprite)
class GameSpriteAdmin(admin.ModelAdmin):
    form = GameSpriteAdminForm
    list_display = ['name', 'sprite_type', 'width', 'height', 'animation_count', 'preview_thumbnail']
    list_filter = ['sprite_type']
    search_fields = ['name']
    inlines = [SpriteAnimationInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'sprite_type', 'width', 'height', 'animation_frames')
        }),
        ('Анимации', {
            'fields': [],  # Поля будут добавлены динамически
            'description': 'Загрузите изображения для каждого состояния анимации'
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        
        if obj and obj.sprite_type:
            # Добавляем динамические поля анимаций
            available_states = GameSprite.ANIMATION_STATES.get(obj.sprite_type, [])
            animation_fields = [f'animation_{state.lower()}' for state in available_states]
            
            fieldsets = list(fieldsets)
            fieldsets[1] = (
                'Анимации',
                {
                    'fields': animation_fields,
                    'description': f'Загрузите изображения для состояний: {", ".join(available_states)}'
                }
            )
        
        return fieldsets
    
    def animation_count(self, obj):
        """Показывает количество загруженных анимаций"""
        total = len(obj.get_available_states())
        loaded = len(obj.animation_paths)
        return f"{loaded}/{total}"
    animation_count.short_description = "Анимации"
    
    def preview_thumbnail(self, obj):
        """Показывает превью первой доступной анимации"""
        if obj.animation_paths:
            first_animation = next(iter(obj.animation_paths.values()))
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px;" />',
                first_animation
            )
        return "Нет изображений"
    preview_thumbnail.short_description = "Превью"
    
    def get_form(self, request, obj=None, **kwargs):
        """Настраиваем форму в зависимости от типа спрайта"""
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(SpriteAnimation)
class SpriteAnimationAdmin(admin.ModelAdmin):
    list_display = ['sprite', 'animation_state', 'order', 'preview_image']
    list_filter = ['sprite__sprite_type', 'animation_state']
    search_fields = ['sprite__name', 'animation_state']
    ordering = ['sprite', 'animation_state', 'order']
    
    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 80px; max-height: 80px;" />',
                obj.image.url
            )
        return "Нет изображения"
    preview_image.short_description = "Превью"