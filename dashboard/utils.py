from django.db.models import Sum, Count, Avg, F, Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
from .models import DashboardMetric, VisitorLog
from orders.models import Order, OrderItem
from products.models import Product, Category
import json


def calculate_daily_metrics(date=None):
    """Рассчитывает дневные метрики"""
    if date is None:
        date = timezone.now().date()
    
    # Рассчитываем метрики
    metrics = DashboardMetric.objects.filter(date=date).first()
    if not metrics:
        metrics = DashboardMetric(date=date)
    
    # Рассчитываем метрики продаж
    orders_today = Order.objects.filter(
        created_at__date=date,
        status__in=['paid', 'completed']
    )
    
    total_revenue = orders_today.aggregate(
        total=Sum('total')
    )['total'] or 0
    
    total_orders = orders_today.count()
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Товары
    total_products = Product.objects.filter(is_active=True).count()
    new_products = Product.objects.filter(
        created_at__date=date,
        is_active=True
    ).count()
    
    # Самый продаваемый товар за день
    top_product = OrderItem.objects.filter(
        order__created_at__date=date,
        order__status__in=['paid', 'completed']
    ).values('product').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold').first()
    
    # Пользователи
    new_users = get_user_model().objects.filter(date_joined__date=date).count()
    total_users = get_user_model().objects.count()
    
    # Конверсия
    visitors_today = VisitorLog.objects.filter(
        timestamp__date=date
    ).values('session_key').distinct().count()
    
    conversion_rate = (total_orders / visitors_today * 100) if visitors_today > 0 else 0
    
    # Обновляем метрики
    metrics.total_revenue = total_revenue
    metrics.total_orders = total_orders
    metrics.average_order_value = average_order_value
    metrics.total_products = total_products
    metrics.new_products = new_products
    metrics.new_users = new_users
    metrics.total_users = total_users
    metrics.conversion_rate = conversion_rate
    
    if top_product:
        metrics.top_selling_product_id = top_product['product']
    
    metrics.save()
    return metrics

def get_sales_data(days=30):
    """Получает данные о продажах за последние N дней"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        metrics = DashboardMetric.objects.filter(date=date).first()
        
        if metrics:
            data.append({
                'date': date.isoformat(),
                'revenue': float(metrics.total_revenue),
                'orders': metrics.total_orders,
                'avg_order': float(metrics.average_order_value)
            })
        else:
            data.append({
                'date': date.isoformat(),
                'revenue': 0,
                'orders': 0,
                'avg_order': 0
            })
    
    return data

def get_category_analytics(days=30):
    """Аналитика продаж по категориям"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    categories = Category.objects.all()
    result = []
    
    for category in categories:
        # Продажи по категории
        sales = OrderItem.objects.filter(
            product__category=category,
            order__created_at__date__gte=start_date,
            order__created_at__date__lte=end_date,
            order__status__in=['paid', 'completed']
        ).aggregate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price'))
        )
        
        # Количество товаров в категории
        product_count = Product.objects.filter(
            category=category,
            is_active=True
        ).count()
        
        result.append({
            'category': category.name,
            'total_sold': sales['total_quantity'] or 0,
            'revenue': float(sales['total_revenue'] or 0),
            'product_count': product_count,
            'avg_price': float(sales['total_revenue'] or 0) / (sales['total_quantity'] or 1)
        })
    
    return result

def get_top_products(limit=10, days=30):
    """Топ товаров по продажам"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    top_products = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__created_at__date__lte=end_date,
        order__status__in=['paid', 'completed']
    ).values(
        'product__id',
        'product__name',
        'product__preview_image',
        'product__category__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_sold')[:limit]
    
    return list(top_products)

def get_user_analytics(days=30):
    """Аналитика пользователей"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Новые пользователи по дням
    new_users_by_day = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        count = get_user_model().objects.filter(date_joined__date=date).count()
        new_users_by_day.append({
            'date': date.isoformat(),
            'count': count
        })
    
    # Активные пользователи
    active_users = Order.objects.filter(
        created_at__date__gte=start_date
    ).values('user').distinct().count()
    
    # Возвращающиеся пользователи
    returning_users = Order.objects.filter(
        created_at__date__gte=start_date
    ).values('user').annotate(
        order_count=Count('id')
    ).filter(order_count__gt=1).count()
    
    return {
        'new_users_by_day': new_users_by_day,
        'active_users': active_users,
        'returning_users': returning_users,
        'total_users': get_user_model().objects.count()
    }

def get_financial_summary():
    """Финансовая сводка"""
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # За сегодня
    today_orders = Order.objects.filter(
        created_at__date=today,
        status__in=['paid', 'completed']
    )
    today_revenue = today_orders.aggregate(total=Sum('total'))['total'] or 0
    today_orders_count = today_orders.count()
    
    # За неделю
    week_orders = Order.objects.filter(
        created_at__date__gte=week_start,
        status__in=['paid', 'completed']
    )
    week_revenue = week_orders.aggregate(total=Sum('total'))['total'] or 0
    
    # За месяц
    month_orders = Order.objects.filter(
        created_at__date__gte=month_start,
        status__in=['paid', 'completed']
    )
    month_revenue = month_orders.aggregate(total=Sum('total'))['total'] or 0
    
    # Ожидающие оплаты
    pending_payments = Order.objects.filter(
        status='pending'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    return {
        'today': {
            'revenue': float(today_revenue),
            'orders': today_orders_count,
            'avg_order': float(today_revenue / today_orders_count) if today_orders_count > 0 else 0
        },
        'week': {
            'revenue': float(week_revenue),
            'avg_daily': float(week_revenue / 7)
        },
        'month': {
            'revenue': float(month_revenue),
            'avg_daily': float(month_revenue / 30)
        },
        'pending_payments': float(pending_payments)
    }