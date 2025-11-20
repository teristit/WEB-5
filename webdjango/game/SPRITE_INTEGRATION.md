# 🎮 Интеграция системы спрайтов / Sprite System Integration

## 📋 Что реализовано / What's Implemented

### ✅ Backend (API)

1. **API Endpoints**:
   - `GET /api/sprites/` - Получение всех спрайтов из базы данных
   - `GET /api/sprite-mapping/` - Получение маппинга символов на типы спрайтов

2. **Модель GameSprite** (models.py):
   ```python
   - name: название спрайта
   - sprite_type: тип (platform, player, enemy, item, background, effect)
   - image: загруженное изображение
   - width, height: размеры
   - animation_frames: количество кадров анимации
   ```

### ✅ Frontend (JavaScript)

**Файл**: `static/js/sprite_loader.js`

**Класс SpriteLoader** с методами:
- `init()` - Загрузка спрайтов из API
- `preloadImages()` - Предзагрузка всех изображений
- `renderSprite(ctx, type, x, y, width, height)` - Рендеринг спрайта
- `renderFallback()` - Отрисовка цветного прямоугольника если спрайт не загружен

---

## 🚀 Как использовать / How to Use

### Шаг 1: Добавить JavaScript в game.html

```html
{% load static %}
<script src="{% static 'js/sprite_loader.js' %}"></script>
```

### Шаг 2: Инициализировать систему перед стартом игры

```javascript
// В функции startGame() или при загрузке страницы:
async function initializeGame() {
    // Инициализация спрайтов
    await spriteLoader.init();
    
    // Загрузка уровня
    loadLevel();
    
    // Старт игрового цикла
    gameLoop();
}

// Вызов при загрузке
initializeGame();
```

### Шаг 3: Заменить ctx.fillRect() на spriteLoader.renderSprite()

**Было (старый код)**:
```javascript
function render() {
    // Рисуем платформы
    ctx.fillStyle = '#8B4513';
    for (let platform of gameState.platforms) {
        ctx.fillRect(platform.x, platform.y, platform.width, platform.height);
    }
    
    // Рисуем предметы
    ctx.fillStyle = '#FFD700';
    for (let item of gameState.collectibles) {
        if (!item.collected) {
            ctx.fillRect(item.x, item.y, item.width, item.height);
        }
    }
}
```

**Стало (новый код со спрайтами)**:
```javascript
function render() {
    // Рисуем платформы
    for (let platform of gameState.platforms) {
        spriteLoader.renderSprite(ctx, 'platform', 
            platform.x, platform.y, platform.width, platform.height);
    }
    
    // Рисуем предметы
    for (let item of gameState.collectibles) {
        if (!item.collected) {
            spriteLoader.renderSprite(ctx, 'item',
                item.x, item.y, item.width, item.height);
        }
    }
    
    // Рисуем врагов
    for (let enemy of gameState.enemies) {
        spriteLoader.renderSprite(ctx, 'enemy',
            enemy.x, enemy.y, enemy.width, enemy.height);
    }
    
    // Рисуем игрока
    spriteLoader.renderSprite(ctx, 'player',
        gameState.player.x, gameState.player.y, 
        gameState.player.width, gameState.player.height);
}
```

---

## 📦 Добавление спрайтов через админ-панель

### Шаг 1: Войти в админку
```
http://localhost:8000/admin/
```

### Шаг 2: Перейти в «Спрайты» (Game Sprites)

### Шаг 3: Добавить новый спрайт

**Пример для платформы**:
- Name: `Brick Platform`
- Sprite type: `platform`
- Image: загрузить PNG файл (50x50px рекомендуется)
- Width: `50`
- Height: `50`
- Animation frames: `1`

**Пример для монеты**:
- Name: `Gold Coin`
- Sprite type: `item`
- Image: загрузить PNG файл (20x20px)
- Width: `20`
- Height: `20`
- Animation frames: `8` (если анимированная)

---

## 🎨 Создание собственных спрайтов

### Рекомендуемые размеры:
- **Platform**: 50x50px
- **Player**: 40x60px
- **Enemy**: 50x50px
- **Item (coin/gem)**: 20x20px

### Форматы:
- PNG с прозрачностью (рекомендуется)
- JPG для фонов

### Инструменты:
- [Piskel](https://www.piskelapp.com/) - онлайн pixel art редактор
- [Aseprite](https://www.aseprite.org/) - профессиональный инструмент
- GIMP / Photoshop

---

## 🔧 Troubleshooting / Решение проблем

### Проблема: Спрайты не загружаются

**Решение**:
1. Проверьте консоль браузера (F12) на ошибки
2. Убедитесь, что API endpoints отвечают:
   ```bash
   curl http://localhost:8000/api/sprites/
   curl http://localhost:8000/api/sprite-mapping/
   ```
3. Проверьте, что `MEDIA_URL` и `MEDIA_ROOT` настроены в `settings.py`

### Проблема: Отображаются цветные прямоугольники вместо спрайтов

Это **нормально** и это fallback-режим! Спрайты не загружены из БД.

**Решение**:
1. Добавьте спрайты через админ-панель
2. Проверьте, что вызвали `spriteLoader.init()` перед игрой

### Проблема: 404 ошибка на изображения спрайтов

**Решение**:
1. Убедитесь, что в `urls.py` добавлено:
   ```python
   from django.conf import settings
   from django.conf.urls.static import static
   
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

---

## 📚 Дополнительные возможности

### Анимация спрайтов (TODO)

Для реализации анимации добавьте в `sprite_loader.js`:

```javascript
renderAnimatedSprite(ctx, type, x, y, width, height, frameIndex) {
    const sprites = this.sprites[type];
    if (!sprites) return this.renderFallback(ctx, type, x, y, width, height);
    
    const sprite = sprites[0];
    const img = this.loadedImages[sprite.id];
    
    if (img && sprite.animation_frames > 1) {
        const frameWidth = img.width / sprite.animation_frames;
        const sx = frameIndex * frameWidth;
        ctx.drawImage(img, sx, 0, frameWidth, img.height,
                      x, y, width, height);
    } else {
        this.renderSprite(ctx, type, x, y, width, height);
    }
}
```

---

## ✅ Checklist для интеграции

- [x] API endpoints созданы (`views.py`)
- [x] URL routes добавлены (`urls.py`)
- [x] `sprite_loader.js` создан
- [ ] Добавить `<script>` тег в `game.html`
- [ ] Вызвать `spriteLoader.init()` при старте
- [ ] Заменить `ctx.fillRect()` на `spriteLoader.renderSprite()`
- [ ] Загрузить тестовые спрайты через админку
- [ ] Протестировать игру

---

## 🎯 Следующие шаги

1. **Загрузить спрайты**: Добавьте хотя бы по 1 спрайту каждого типа через админку
2. **Интегрировать в game.html**: Добавьте вызовы из примеров выше
3. **Создать красивые спрайты**: Используйте Piskel или Aseprite
4. **Добавить анимацию**: Реализуйте `renderAnimatedSprite()`
5. **Сделать редактор уровней**: Drag-and-drop спрайтов на canvas

---

Создано: 2025-11-20 | Django Platformer Game
