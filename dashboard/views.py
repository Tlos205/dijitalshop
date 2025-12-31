from django.db.models import Count, Q, F, Sum, Avg, FloatField, ExpressionWrapper
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from datetime import timedelta, datetime
import json

from .utils import (
    calculate_daily_metrics,
    get_sales_data,
    get_category_analytics,
    get_top_products,
    get_user_analytics,
    get_financial_summary
)
from orders.models import Order, OrderItem
from products.models import Product, Category

@staff_member_required
def dashboard_home(request):
    """Главная страница дашборда"""
    
    # Рассчитываем сегодняшние метрики
    calculate_daily_metrics()
    
    # Получаем данные
    today = timezone.now().date()
    
    # Последние заказы
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Новые пользователи
    new_users = get_user_model().objects.order_by('-date_joined')[:5]
    
    # Популярные товары
    popular_products = get_top_products(limit=5)
    
    # Финансовая сводка
    financial_summary = get_financial_summary()
    
    # Статистика по статусам заказов
    order_status_stats = Order.objects.aggregate(
        pending=Count('id', filter=Q(status='pending')),
        paid=Count('id', filter=Q(status='paid')),
        completed=Count('id', filter=Q(status='completed')),
        cancelled=Count('id', filter=Q(status='cancelled'))
    )
    
    context = {
        'page_title': 'Главная панель',
        'recent_orders': recent_orders,
        'new_users': new_users,
        'popular_products': popular_products,
        'financial_summary': financial_summary,
        'order_status_stats': order_status_stats,
        'today': today,
    }
    
    return render(request, 'dashboard/home.html', context)

@staff_member_required
def dashboard_sales(request):
    """Аналитика продаж"""
    days = int(request.GET.get('days', 30))
    
    # Данные для графиков
    sales_data = get_sales_data(days)
    category_data = get_category_analytics(days)
    
    # Топ товары
    top_products = get_top_products(limit=20, days=days)
    
    # Распределение по времени суток
    hour_distribution = []
    for hour in range(24):
        orders_count = Order.objects.filter(
            created_at__hour=hour,
            created_at__date__gte=timezone.now().date() - timedelta(days=days),
            status__in=['paid', 'completed']
        ).count()
        hour_distribution.append({
            'hour': hour,
            'count': orders_count
        })
    
    context = {
        'page_title': 'Аналитика продаж',
        'sales_data': json.dumps(sales_data),
        'category_data': json.dumps(category_data),
        'top_products': top_products,
        'hour_distribution': json.dumps(hour_distribution),
        'days': days,
    }
    
    return render(request, 'dashboard/sales.html', context)

@staff_member_required
def dashboard_products(request):
    """Аналитика товаров"""
    
    # Статистика по товарам
    product_stats = {
        'total': Product.objects.count(),
        'active': Product.objects.filter(is_active=True).count(),
        'inactive': Product.objects.filter(is_active=False).count(),
        'featured': Product.objects.filter(is_featured=True).count(),
        'with_discount': Product.objects.filter(discount_price__isnull=False).count(),
    }
    
    # Товары без продаж
    products_without_sales = Product.objects.filter(
        sales_count=0,
        is_active=True
    ).order_by('-created_at')[:10]
    
    # Товары с низким рейтингом просмотров/продаж
    # Используем ExpressionWrapper для вычисления конверсии в запросе
    low_performing_products = Product.objects.filter(
        is_active=True
    ).annotate(
        # Вычисляем конверсию: (продажи / просмотры) * 100
        conversion_rate=ExpressionWrapper(
            F('sales_count') / F('view_count') * 100,
            output_field=FloatField()
        )
    ).filter(
        Q(view_count__gt=0),  # Исключаем товары с нулевыми просмотрами
        Q(conversion_rate__lt=1) | Q(conversion_rate__isnull=True),  # Конверсия < 1% или null
        view_count__gt=100  # Но с просмотрами > 100
    ).order_by('conversion_rate')[:10]
    
    # ВЫЧИСЛЯЕМ КОНВЕРСИЮ ДЛЯ КАЖДОГО ТОВАРА В PYTHON
    for product in low_performing_products:
        if product.view_count and product.view_count > 0:
            product.calculated_conversion = round(
                (product.sales_count or 0) / product.view_count * 100, 
                1
            )
        else:
            product.calculated_conversion = 0.0
    
    # Распределение по категориям
    category_distribution = []
    for category in Category.objects.all():
        count = Product.objects.filter(category=category, is_active=True).count()
        if count > 0:
            category_distribution.append({
                'name': category.name,
                'count': count
            })
    
    context = {
        'page_title': 'Аналитика товаров',
        'product_stats': product_stats,
        'products_without_sales': products_without_sales,
        'low_performing_products': low_performing_products,
        'category_distribution': json.dumps(category_distribution),
        'categories': Category.objects.all(),  # Добавляем для экспорта
    }
    
    return render(request, 'dashboard/products.html', context)

@staff_member_required
def dashboard_users(request):
    """Аналитика пользователей"""

    User = get_user_model()
    user_analytics = get_user_analytics()
    
    # Распределение пользователей по активности
    user_activity = {
        'active_this_month': Order.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('user').distinct().count(),
        'never_ordered': User.objects.filter(
            orders__isnull=True  # ИСПРАВЛЕНО
        ).count(),
        'one_time_buyers': User.objects.annotate(
            order_count=Count('orders')  # ИСПРАВЛЕНО
        ).filter(order_count=1).count(),
        'repeat_buyers': User.objects.annotate(
            order_count=Count('orders')  # ИСПРАВЛЕНО
        ).filter(order_count__gt=1).count(),
    }
    
    # География пользователей (заглушка - можно подключить IP geolocation)
    # user_locations = [...]  # Для реального проекта
    
    # Распределение по дате регистрации
    registration_stats = []
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        month_start = date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = get_user_model().objects.filter(
            date_joined__gte=month_start,
            date_joined__lte=month_end
        ).count()
        
        registration_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    
    registration_stats.reverse()
    
    # Список пользователей с аналитикой
    users_list = User.objects.annotate(
        order_count=Count('orders'),  # ИСПРАВЛЕНО
        total_spent=Sum('orders__total', filter=Q(orders__status__in=['paid', 'completed']))  # ИСПРАВЛЕНО
    ).order_by('-date_joined')[:50]
    
    # Топ покупателей
    top_customers = User.objects.annotate(
        order_count=Count('orders', filter=Q(orders__status__in=['paid', 'completed'])),  # ИСПРАВЛЕНО
        total_spent=Sum('orders__total', filter=Q(orders__status__in=['paid', 'completed']))  # ИСПРАВЛЕНО
    ).filter(order_count__gt=0).order_by('-total_spent')[:5]
    
    # Расчетные метрики
    avg_order_value = Order.objects.filter(
        status__in=['paid', 'completed']
    ).aggregate(avg=Avg('total'))['avg'] or 0
    
    # Расчет LTV и CAC (примерные значения)
    avg_ltv = 1500.00
    cac = 450.00
    ltv_cac_ratio = avg_ltv / cac if cac > 0 else 0
    
    # Retention и Churn (примерные)
    retention_rate = 65.5
    churn_rate = 34.5
    
    context = {
        'page_title': 'Аналитика пользователей',
        'user_analytics': user_analytics,
        'user_activity': user_activity,
        'registration_stats': json.dumps(registration_stats),
        'total_users': get_user_model().objects.count(),
        'users_list': users_list,
        'top_customers': top_customers,
        'avg_order_value': avg_order_value,
        'avg_ltv': avg_ltv,
        'cac': cac,
        'ltv_cac_ratio': ltv_cac_ratio,
        'retention_rate': retention_rate,
        'churn_rate': churn_rate,
        'inactive_users': get_user_model().objects.filter(
            last_login__lt=timezone.now() - timedelta(days=30)
        ).count(),
    }
    
    return render(request, 'dashboard/users.html', context)

@staff_member_required
def dashboard_finance(request):
    """Финансовая аналитика"""
    
    # Доход по месяцам
    monthly_revenue = []
    for i in range(6):
        month_start = (timezone.now() - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        revenue = Order.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end,
            status__in=['paid', 'completed']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue)
        })
    
    monthly_revenue.reverse()
    
    # Налоги и комиссии (примерные расчеты)
    tax_rate = 0.20  # 20% НДС
    commission_rate = 0.03  # 3% комиссия платежной системы
    
    total_revenue = sum(item['revenue'] for item in monthly_revenue)
    estimated_tax = total_revenue * tax_rate
    estimated_commission = total_revenue * commission_rate
    estimated_profit = total_revenue - estimated_tax - estimated_commission
    
    # Ожидаемые платежи
    pending_orders = Order.objects.filter(status='pending')
    expected_payments = pending_orders.aggregate(total=Sum('total'))['total'] or 0
    
    # Прогноз на следующий месяц (простой)
    avg_monthly_growth = 0.10  # 10% рост
    next_month_forecast = monthly_revenue[-1]['revenue'] * (1 + avg_monthly_growth)
    
    avg_monthly_revenue = sum(item['revenue'] for item in monthly_revenue) / len(monthly_revenue) if monthly_revenue else 0
    
    # Расчетные метрики
    monthly_growth = 15.0  # Примерный рост
    
    # Transaction data (пример)
    transactions = [
        {
            'id': 1,
            'date': timezone.now() - timedelta(days=2),
            'type': 'Вывод средств',
            'type_color': 'warning',
            'description': 'Вывод на карту **** 1234',
            'amount': -15000.00,
            'status': 'Завершено',
            'status_color': 'success',
            'balance_after': 85000.00,
            'order_number': None
        },
        {
            'id': 2,
            'date': timezone.now() - timedelta(days=1),
            'type': 'Продажа',
            'type_color': 'success',
            'description': 'Продажа товара "Шаблон сайта"',
            'amount': 2500.00,
            'status': 'Завершено',
            'status_color': 'success',
            'balance_after': 87500.00,
            'order_number': 'ORD-20231205-1234'
        },
    ]
    
    # Примерные расходы
    hosting_cost = 5000.00
    marketing_cost = 10000.00
    
    context = {
        'page_title': 'Финансовая аналитика',
        'monthly_revenue': json.dumps(monthly_revenue),
        'total_revenue': total_revenue,
        'estimated_tax': estimated_tax,
        'estimated_commission': estimated_commission,
        'estimated_profit': estimated_profit,
        'expected_payments': expected_payments,
        'next_month_forecast': next_month_forecast,
        'tax_rate': tax_rate * 100,
        'commission_rate': commission_rate * 100,
        'avg_monthly_revenue': avg_monthly_revenue,
        'monthly_growth': monthly_growth,
        'transactions': transactions,
        'hosting_cost': hosting_cost,
        'marketing_cost': marketing_cost,
        'available_for_withdrawal': 100000.00,
        'forecast_3m': next_month_forecast * 1.15 * 1.15,
        'conversion_rate': 2.5,
        'cac': 450.00,
        'ltv': 1500.00,
        'ltv_cac_ratio': 3.3,
    }
    
    return render(request, 'dashboard/finance.html', context)

@staff_member_required
def dashboard_reports(request):
    """Отчеты"""
    
    # Доступные отчеты   
    reports = [
        {
            'id': 'daily_sales',
            'name': 'Ежедневный отчет по продажам',
            'description': 'Подробная информация о продажах за день',
            'format': 'PDF/Excel',
            'schedule': 'Ежедневно',
            'icon': 'chart-line'
        },
        {
            'id': 'monthly_finance',
            'name': 'Месячный финансовый отчет',
            'description': 'Выручка, расходы, прибыль',
            'format': 'PDF/Excel',
            'schedule': 'Ежемесячно',
            'icon': 'wallet'
        },
        {
            'id': 'user_activity',
            'name': 'Отчет по активности пользователей',
            'description': 'Новые пользователи, конверсия, retention',
            'format': 'PDF',
            'schedule': 'Еженедельно',
            'icon': 'users'
        },
        {
            'id': 'product_performance',
            'name': 'Отчет по эффективности товаров',
            'description': 'Продажи, просмотры, конверсия по товарам',
            'format': 'Excel',
            'schedule': 'Ежемесячно',
            'icon': 'box'
        },
        {
            'id': 'category_analysis',
            'name': 'Анализ по категориям',
            'description': 'Продажи и выручка по категориям',
            'format': 'PDF/Excel',
            'schedule': 'Еженедельно',
            'icon': 'folder'
        },
        {
            'id': 'marketing',
            'name': 'Отчет по маркетингу',
            'description': 'Эффективность рекламных кампаний',
            'format': 'Excel',
            'schedule': 'Ежемесячно',
            'icon': 'bullhorn'
        },
    ]
    
    # Запланированные отчеты (пример)
    scheduled_reports = [
        {
            'id': 1,
            'report_name': 'Ежедневный отчет по продажам',
            'description': 'Автоматическая отправка в 09:00',
            'schedule': 'Ежедневно',
            'format': 'PDF',
            'recipients': ['owner@digimart.ru', 'manager@digimart.ru'],
            'last_run': timezone.now() - timedelta(hours=3),
            'is_active': True
        },
    ]
    
    # История отчетов (пример)
    report_history = [
        {
            'id': 1,
            'created_at': timezone.now() - timedelta(days=1),
            'report_name': 'Ежедневный отчет по продажам',
            'period': timezone.now().strftime('%Y-%m-%d'),
            'format': 'PDF',
            'file_size': '1.2 MB',
            'status': 'success',
            'recipient_count': 2,
            'download_url': '#'
        },
    ]
    
    context = {
        'page_title': 'Отчеты',
        'reports': reports,
        'scheduled_reports': scheduled_reports,
        'report_history': report_history,
    }
    
    return render(request, 'dashboard/reports.html', context)

# API endpoints для обновления данных без перезагрузки страницы
@staff_member_required
def api_dashboard_stats(request):
    """API для получения статистики дашборда"""
    days = int(request.GET.get('days', 7))
    
    data = {
        'sales_data': get_sales_data(days),
        'financial_summary': get_financial_summary(),
        'top_products': get_top_products(5, days),
    }
    
    return JsonResponse(data)

@staff_member_required 
def api_generate_report(request, report_id):
    """API для генерации отчетов"""
    # Здесь будет логика генерации PDF/Excel отчетов
    # Пока возвращаем JSON с данными
    
    if report_id == 'daily_sales':
        data = get_sales_data(1)
    elif report_id == 'monthly_finance':
        data = get_financial_summary()
    else:
        data = {'error': 'Report not found'}
    
    return JsonResponse(data)






@staff_member_required
def manage_products(request):
    """Управление товарами и категориями"""
    # Получаем все товары с дополнительной информацией
    products = Product.objects.select_related('category').all().order_by('-created_at')[:50]
    
    # Получаем категории с количеством товаров
    categories = Category.objects.annotate(
        product_count=Count('product'),
        total_sales=Sum('product__sales_count')
    ).order_by('name')
    
    # Список типов товаров
    product_types = Product.TYPE_CHOICES
    
    # Товары требующие обновления
    needs_update = Product.objects.filter(
        is_active=True
    ).exclude(
        updated_at__gte=timezone.now() - timedelta(days=90)
    )[:10]
    
    context = {
        'page_title': 'Управление товарами',
        'products': products,
        'categories': categories,
        'product_types': product_types,
        'products_count': Product.objects.count(),
        'categories_count': Category.objects.count(),
        'active_products': Product.objects.filter(is_active=True).count(),
        'total_products': Product.objects.count(),
        'low_performance_count': Product.objects.filter(sales_count=0, is_active=True).count(),
        'needs_update': needs_update,
    }
    
    return render(request, 'dashboard/manage_products.html', context)


# API endpoints
@require_GET
@staff_member_required
def api_products(request):
    """API для получения списка товаров"""
    products = Product.objects.select_related('category').all()
    
    # Фильтрация
    status = request.GET.get('status', 'all')
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)
    elif status == 'featured':
        products = products.filter(is_featured=True)
    elif status == 'discount':
        products = products.filter(discount_price__isnull=False)
    elif status == 'no_sales':
        products = products.filter(sales_count=0)
    
    # Сортировка
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        products = products.order_by('created_at')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'sales_desc':
        products = products.order_by('-sales_count')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Поиск
    search = request.GET.get('search', '')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__icontains=search)
        )
    
    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'category': product.category.name,
            'price': float(product.price),
            'discount_price': float(product.discount_price) if product.discount_price else None,
            'sales_count': product.sales_count,
            'view_count': product.view_count,
            'is_active': product.is_active,
            'is_featured': product.is_featured,
            'preview_image': product.preview_image.url if product.preview_image else None,
            'created_at': product.created_at.strftime('%d.%m.%Y'),
        })
    
    return JsonResponse({'success': True, 'products': data})

@require_GET
@staff_member_required
def api_product_detail(request, product_id):
    """API для получения деталей товара"""
    product = get_object_or_404(Product, id=product_id)
    
    data = {
        'id': product.id,
        'name': product.name,
        'category_id': product.category.id,
        'product_type': product.product_type,
        'price': float(product.price),
        'discount_price': float(product.discount_price) if product.discount_price else None,
        'short_description': product.short_description,
        'description': product.description,
        'detailed_description': product.detailed_description,
        'tags': product.tags,
        'file_size': product.file_size,
        'file_format': product.file_format,
        'version': product.version,
        'compatibility': product.compatibility,
        'is_active': product.is_active,
        'is_featured': product.is_featured,
    }
    
    return JsonResponse({'success': True, 'product': data})

@require_POST
@staff_member_required
def api_toggle_product_status(request, product_id):
    """API для переключения статуса товара"""
    try:
        product = Product.objects.get(id=product_id)
        data = json.loads(request.body)
        product.is_active = data.get('is_active', not product.is_active)
        product.save()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден'})

@require_POST
@staff_member_required
def api_bulk_product_action(request):
    """API для массовых действий с товарами"""
    try:
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
        action = data.get('action')
        
        products = Product.objects.filter(id__in=product_ids)
        
        if action == 'activate':
            products.update(is_active=True)
        elif action == 'deactivate':
            products.update(is_active=False)
        elif action == 'featured':
            products.update(is_featured=True)
        elif action == 'unfeatured':
            products.update(is_featured=False)
        elif action == 'delete':
            products.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
def api_delete_product(request, product_id):
    """API для удаления товара"""
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден'})

# Аналогичные API для категорий
@require_POST
@staff_member_required
def api_categories(request):
    """API для добавления категории"""
    try:
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            return JsonResponse({'success': True, 'category_id': category.id})
        else:
            return JsonResponse({'success': False, 'error': 'Неверные данные формы'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_GET
@staff_member_required
def api_category_detail(request, category_id):
    """API для получения деталей категории"""
    category = get_object_or_404(Category, id=category_id)
    
    data = {
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'description': category.description,
        'is_active': category.is_active,
    }
    
    return JsonResponse({'success': True, 'category': data})

@require_POST
@staff_member_required
def api_toggle_category_status(request, category_id):
    """API для переключения статуса категории"""
    try:
        category = Category.objects.get(id=category_id)
        data = json.loads(request.body)
        category.is_active = data.get('is_active', not category.is_active)
        category.save()
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Категория не найдена'})

@staff_member_required
def api_delete_category(request, category_id):
    """API для удаления категории"""
    try:
        category = Category.objects.get(id=category_id)
        # Проверяем, нет ли товаров в категории
        if category.product_set.exists():
            return JsonResponse({
                'success': False, 
                'error': 'Нельзя удалить категорию с товарами. Переместите товары в другую категорию.'
            })
        category.delete()
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Категория не найдена'})

@require_POST
@staff_member_required
def api_import_products(request):
    """API для импорта товаров"""
    # Здесь будет логика импорта из CSV/Excel
    return JsonResponse({'success': True, 'message': 'Импорт начат'})

@require_GET
@staff_member_required
def api_export_products(request):
    """API для экспорта товаров"""
    # Здесь будет логика экспорта в CSV/Excel
    return JsonResponse({'success': True, 'message': 'Экспорт начат'})