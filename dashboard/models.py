# dashboard/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from products.models import Product, Category
from orders.models import Order, OrderItem

class DashboardMetric(models.Model):
    """Метрики для дашборда"""
    date = models.DateField(unique=True, verbose_name="Дата")
    
    # Продажи
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Выручка")
    total_orders = models.IntegerField(default=0, verbose_name="Количество заказов")
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Средний чек")
    
    # Товары
    total_products = models.IntegerField(default=0, verbose_name="Всего товаров")
    new_products = models.IntegerField(default=0, verbose_name="Новых товаров")
    top_selling_product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Топ товар")
    
    # Пользователи
    new_users = models.IntegerField(default=0, verbose_name="Новых пользователей")
    total_users = models.IntegerField(default=0, verbose_name="Всего пользователей")
    
    # Конверсия
    conversion_rate = models.FloatField(default=0, verbose_name="Конверсия")
    cart_abandonment_rate = models.FloatField(default=0, verbose_name="Брошенные корзины")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Метрика дашборда"
        verbose_name_plural = "Метрики дашборда"
        ordering = ['-date']
    
    def __str__(self):
        return f"Метрики за {self.date}"

class VisitorLog(models.Model):
    """Лог посещений сайта"""
    session_key = models.CharField(max_length=40)
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    page_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Лог посещения"
        verbose_name_plural = "Логи посещений"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Посещение {self.page_url} в {self.timestamp}"

class SaleAnalytics(models.Model):
    """Аналитика продаж по категориям"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField()
    
    total_sales = models.IntegerField(default=0, verbose_name="Продажи (шт)")
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Выручка")
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Средняя цена")
    
    class Meta:
        verbose_name = "Аналитика продаж"
        verbose_name_plural = "Аналитика продаж"
        unique_together = ['category', 'date']
        ordering = ['-date', 'category']
    
    def __str__(self):
        return f"{self.category.name} - {self.date}"