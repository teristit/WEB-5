# Django Platformer Game

Переработанная версия 2D платформера с оригинальной игры pygame на Django с улучшенным геймплеем.

## Оригинальная игра

Исходная игра была найдена в репозитории: https://github.com/teristit/game

Основные компоненты оригинальной игры:
- `platformer.py` - основной модуль игры
- `kybik.py` - модуль с игровой логикой
- `data/platformerimage/` - спрайты и анимации
- `levels/` - файлы уровней
- `music/` - звуковые файлы

## Структура Django проекта

```
django_platformer/
├── manage.py
├── requirements.txt
├── platformer_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── game/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── consumers.py
│   └── migrations/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
    └── game/
```

## Улучшения в Django версии

1. **Веб-интерфейс**: Игра запускается в браузере
2. **Сохранение прогресса**: Результаты сохраняются в базу данных
3. **Мультиплеер**: Поддержка WebSocket для многопользовательской игры
4. **Система достижений**: Трекинг достижений игрока
5. **Рейтинги**: Таблица лидеров
6. **Адаптивный дизайн**: Работает на разных устройствах

## Установка

1. Клонируйте репозиторий
2. Установите зависимости: `pip install -r requirements.txt`
3. Выполните миграции: `python manage.py migrate`
4. Запустите сервер: `python manage.py runserver`

## Запуск

Откройте http://localhost:8000 в браузере для игры.

## Особенности

- Canvas-based рендеринг в браузере
- WebSocket для реального времени
- RESTful API для сохранения состояния
- Адаптация оригинальных спрайтов и анимаций