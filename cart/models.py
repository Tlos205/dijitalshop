# cart/models.py
from django.db import models
from django.conf import settings
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class Cart(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Пользователь"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
    
    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.username}"
        return f"Корзина (сессия: {self.session_key})"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    
    @property
    def total_price(self):
        return self.product.current_price * self.quantity