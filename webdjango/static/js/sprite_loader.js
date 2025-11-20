/**
 * Sprite Loading System for Django Platformer
 * Система загрузки спрайтов из базы данных
 * 
 * Usage / Использование:
 * 1. Добавьте этот файл в game.html:
 *    <script src="{% static 'js/sprite_loader.js' %}"></script>
 * 
 * 2. Инициализируйте систему перед стартом игры:
 *    await SpriteLoader.init();
 * 
 * 3. Рендер спрайтов вместо ctx.fillRect:
 *    SpriteLoader.renderSprite(ctx, 'platform', x, y, width, height);
 */

class SpriteLoader {
    constructor() {
        this.sprites = {};
        this.spriteMapping = {};
        this.loadedImages = {};
        this.isLoaded = false;
    }

    async init() {
        try {
            // Загрузка маппинга
            const mappingResponse = await fetch('/api/sprite-mapping/');
            const mappingData = await mappingResponse.json();
            this.spriteMapping = mappingData.mapping;

            // Загрузка спрайтов
            const spritesResponse = await fetch('/api/sprites/');
            const spritesData = await spritesResponse.json();
            
            // Группировка по типам
            spritesData.sprites.forEach(sprite => {
                if (!this.sprites[sprite.sprite_type]) {
                    this.sprites[sprite.sprite_type] = [];
                }
                this.sprites[sprite.sprite_type].push(sprite);
            });

            // Предзагрузка изображений
            await this.preloadImages();
            
            this.isLoaded = true;
            console.log('Спрайты загружены:', this.sprites);
            return true;
        } catch (error) {
            console.error('Ошибка загрузки спрайтов:', error);
            return false;
        }
    }

    async preloadImages() {
        const promises = [];
        
        for (const type in this.sprites) {
            this.sprites[type].forEach(sprite => {
                if (sprite.image_url) {
                    const promise = new Promise((resolve, reject) => {
                        const img = new Image();
                        img.onload = () => resolve({ id: sprite.id, img });
                        img.onerror = reject;
                        img.src = sprite.image_url;
                    });
                    promises.push(promise);
                }
            });
        }

        const results = await Promise.all(promises);
        results.forEach(({ id, img }) => {
            this.loadedImages[id] = img;
        });
    }

    renderSprite(ctx, type, x, y, width, height) {
        if (!this.isLoaded) {
            // Fallback: рисуем цветной прямоугольник
            this.renderFallback(ctx, type, x, y, width, height);
            return;
        }

        const sprites = this.sprites[type];
        if (!sprites || sprites.length === 0) {
            this.renderFallback(ctx, type, x, y, width, height);
            return;
        }

        // Берем первый спрайт для данного типа
        const sprite = sprites[0];
        const img = this.loadedImages[sprite.id];

        if (img) {
            ctx.drawImage(img, x, y, width, height);
        } else {
            this.renderFallback(ctx, type, x, y, width, height);
        }
    }

    renderFallback(ctx, type, x, y, width, height) {
        // Цвета по умолчанию для разных типов
        const colors = {
            'platform': '#8B4513',
            'player': '#0000FF',
            'enemy': '#FF4500',
            'item': '#FFD700'
        };
        
        ctx.fillStyle = colors[type] || '#888888';
        ctx.fillRect(x, y, width, height);
    }

    getSpriteTypeForSymbol(symbol) {
        return this.spriteMapping[symbol] || null;
    }
}

// Глобальный экземпляр
const spriteLoader = new SpriteLoader();

// Экспорт
 if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpriteLoader;
}
