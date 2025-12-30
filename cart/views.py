from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .utils import (
    get_cart, add_to_cart, remove_from_cart, 
    update_cart_item, get_cart_items, clear_cart
)

def cart_detail(request):
    cart_items = get_cart_items(request)
    cart_total = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    
    return render(request, 'cart/cart_detail.html', context)

@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    add_to_cart(request, product_id, quantity)
    
    messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    
    return redirect('cart_detail')

@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    remove_from_cart(request, product_id)
    
    messages.success(request, f'Товар "{product.name}" удален из корзины')
    
    return redirect('cart_detail')

@require_POST
def cart_update(request, product_id):
    quantity = int(request.POST.get('quantity', 1))
    
    update_cart_item(request, product_id, quantity)
    
    messages.success(request, 'Корзина обновлена')
    
    return redirect('cart_detail')

@require_POST
def cart_clear(request):
    clear_cart(request)
    
    messages.success(request, 'Корзина очищена')
    
    return redirect('cart_detail')