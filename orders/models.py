from django.db import models
from django.conf import settings
from products.models import Product
from django.contrib.auth import get_user_model

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(
        get_user_model(), 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name="Пользователь"
    )
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Номер заказа")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    
    # Информация о покупателе
    email = models.EmailField(verbose_name="Email")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    
    # Стоимость
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма товаров")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Налог")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итого")
    
    # Платежная информация
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Метод оплаты")
    payment_id = models.CharField(max_length=100, blank=True, verbose_name="ID платежа")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата оплаты")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.order_number}"
    
    def generate_order_number(self):
        import datetime
        return f"ORD-{datetime.datetime.now().strftime('%Y%m%d')}-{self.id:06d}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    product_name = models.CharField(max_length=200, verbose_name="Название товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"
    
    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"
    
    @property
    def total_price(self):
        return self.price * self.quantity