# create_test_data_fixed.py
import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digimart.settings')
django.setup()

from products.models import Category, Product, ProductFeature
from django.contrib.auth.models import User

def create_test_data():
    # Создаем категории с английскими slug
    categories_data = [
        {
            'name': 'Шаблоны сайтов', 
            'slug': 'website-templates',
            'description': 'Готовые шаблоны для различных типов сайтов'
        },
        {
            'name': 'Графика и дизайн', 
            'slug': 'graphics-design',
            'description': 'Векторная графика, иконки, шрифты'
        },
        {
            'name': 'Электронные книги', 
            'slug': 'ebooks',
            'description': 'Книги и руководства в цифровом формате'
        },
        {
            'name': 'Программное обеспечение', 
            'slug': 'software',
            'description': 'Скрипты, плагины и программы'
        },
        {
            'name': 'Онлайн-курсы', 
            'slug': 'online-courses',
            'description': 'Обучающие материалы и видеокурсы'
        },
        {
            'name': 'Музыка и звуки', 
            'slug': 'music-sounds',
            'description': 'Музыкальные композиции и звуковые эффекты'
        },
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        categories.append(category)
        print(f'{"Создана" if created else "Найдена"} категория: {category.name} (slug: {category.slug})')
    
    # Создаем тестового пользователя
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Тест',
            'last_name': 'Пользователь'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print('Создан тестовый пользователь')
    else:
        print('Тестовый пользователь уже существует')
    
    # Создаем тестовые товары
    products_data = [
        {
            'name': 'Шаблон интернет-магазина "E-Shop"',
            'category': categories[0],
            'price': 2990,
            'discount_price': 1990,
            'description': 'Современный шаблон интернет-магазина на Bootstrap 5',
            'product_type': 'template',
            'features': [
                {'name': 'Адаптивность', 'value': 'Да'},
                {'name': 'Страниц', 'value': '15'},
                {'name': 'Фреймворк', 'value': 'Bootstrap 5'},
            ]
        },
        {
            'name': 'Набор бизнес-иконок',
            'category': categories[1],
            'price': 1490,
            'description': 'Набор из 100 векторных иконок для бизнеса',
            'product_type': 'graphics',
            'features': [
                {'name': 'Количество', 'value': '100 иконок'},
                {'name': 'Формат', 'value': 'SVG, PNG'},
                {'name': 'Размер', 'value': '512x512px'},
            ]
        },
        {
            'name': 'Книга "Python для начинающих"',
            'category': categories[2],
            'price': 990,
            'description': 'Полное руководство по Python для новичков',
            'product_type': 'ebook',
            'features': [
                {'name': 'Страниц', 'value': '350'},
                {'name': 'Формат', 'value': 'PDF, EPUB'},
                {'name': 'Язык', 'value': 'Русский'},
            ]
        },
        {
            'name': 'Скрипт блога на Django',
            'category': categories[3],
            'price': 4990,
            'discount_price': 3990,
            'description': 'Готовый скрипт блога с админ-панелью',
            'product_type': 'software',
            'features': [
                {'name': 'Версия Django', 'value': '4.2'},
                {'name': 'База данных', 'value': 'PostgreSQL'},
                {'name': 'Документация', 'value': 'Включена'},
            ]
        },
        {
            'name': 'Курс "Веб-разработка с нуля"',
            'category': categories[4],
            'price': 8990,
            'description': 'Полный курс по веб-разработке',
            'product_type': 'course',
            'features': [
                {'name': 'Уроков', 'value': '50'},
                {'name': 'Длительность', 'value': '40 часов'},
                {'name': 'Сертификат', 'value': 'Да'},
            ]
        },
    ]
    
    for prod_data in products_data:
        features = prod_data.pop('features', [])
        
        # Генерируем slug для товара
        slug = slugify(prod_data['name'])
        
        # Проверяем, существует ли уже товар с таким slug
        existing_product = Product.objects.filter(slug=slug).first()
        if existing_product:
            print(f'Товар уже существует: {prod_data["name"]}')
            continue
            
        try:
            # Добавляем slug в данные товара
            prod_data['slug'] = slug
            
            # Создаем товар
            product = Product.objects.create(**prod_data)
            
            # Добавляем характеристики
            for feature_data in features:
                ProductFeature.objects.create(
                    product=product,
                    **feature_data
                )
            
            print(f'Создан товар: {product.name} (slug: {product.slug})')
        except Exception as e:
            print(f'Ошибка при создании товара {prod_data["name"]}: {e}')

if __name__ == '__main__':
    create_test_data()
    print('Тестовые данные успешно созданы!')