# Руководство по использованию спрайт-шитов (Sprite Sheets)

## Структура спрайт-шита

Для анимации игрока используется PNG-файл с расположенными горизонтально кадрами анимации.

### Требования к файлу:
- **Формат**: PNG с прозрачным фоном
- **Размер кадра**: 40x60 пикселей (ширина x высота)
- **Расположение**: все кадры в одной строке, слева направо

### Структура кадров:
```
[Кадры 0-7]   [Кадры 8-15]  [Кадр 16] [Кадр 17] [Кадр 18] [Кадр 19] [Кадр 20] [Кадр 21]
Ходьба вправо  Ходьба влево  Прыжок↑   Прыжок←   Падение→  Падение←  Idle→     Idle←
```

## Размещение файла

Поместите PNG-файл в:
```
webdjango/static/images/player_spritesheet.png
```

## Параметры анимации в коде

```javascript
const SPRITE_CONFIG = {
    imagePath: '/static/images/player_spritesheet.png',
    frameWidth: 40,
    frameHeight: 60,
    animations: {
        walk_right: { startFrame: 0, endFrame: 7 },
        walk_left: { startFrame: 8, endFrame: 15 },
        jump_right: { startFrame: 16, endFrame: 16 },
        jump_left: { startFrame: 17, endFrame: 17 },
        fall_right: { startFrame: 18, endFrame: 18 },
        fall_left: { startFrame: 19, endFrame: 19 },
        idle_right: { startFrame: 20, endFrame: 20 },
        idle_left: { startFrame: 21, endFrame: 21 }
    }
};
```

## Как создать свой спрайт-шит

1. Создайте изображение размером **880x60** пикселей (22 кадра по 40px)
2. Нарисуйте кадры анимации согласно структуре выше
3. Экспортируйте как PNG с прозрачным фоном
4. Сохраните как `player_spritesheet.png` в папке `webdjango/static/images/`

## Альтернативный вариант

Если у вас спрайт-шит с другой структурой, измените параметры в `SPRITE_CONFIG`:
- `startFrame` - номер первого кадра анимации
- `endFrame` - номер последнего кадра анимации
- `frameWidth/frameHeight` - размеры одного кадра