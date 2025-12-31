from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.utils import get_cart_items, clear_cart
from .models import Order, OrderItem
from .forms import OrderForm

@login_required
def create_order(request):
    cart_items = get_cart_items(request)
    
    if not cart_items:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart_detail')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.user = request.user
            
            # Рассчитываем суммы
            subtotal = sum(item.total_price for item in cart_items)
            tax = subtotal * 0.20  # Пример: 20% налог
            total = subtotal + tax
            
            order.subtotal = subtotal
            order.tax = tax
            order.total = total
            
            # Генерируем номер заказа
            order.save()
            order.order_number = order.generate_order_number()
            order.save()
            
            # Создаем товары в заказе
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    price=cart_item.product.current_price,
                    quantity=cart_item.quantity
                )
            
            # Очищаем корзину
            clear_cart(request)
            
            messages.success(request, f'Заказ #{order.order_number} успешно создан!')
            return redirect('order_detail', order_id=order.id)
    else:
        # Предзаполняем форму данными пользователя
        initial_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = OrderForm(initial=initial_data)
    
    # Рассчитываем итоговые суммы для отображения
    subtotal = sum(item.total_price for item in cart_items)
    tax = subtotal * 0.20
    total = subtotal + tax
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
    }
    
    return render(request, 'orders/create_order.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/order_list.html', context)