# cart/utils.py
from django.conf import settings
from .models import Cart, CartItem
from products.models import Product


def get_cart(request):
    cart = None
    cart_id = request.session.get('cart_id')
    
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            cart = None
    
    if not cart:
        if request.user.is_authenticated:
            # Пытаемся найти корзину пользователя
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # Создаем новую корзину для анонимного пользователя
            cart = Cart.objects.create(session_key=request.session.session_key)
        
        request.session['cart_id'] = cart.id
    
    return cart

def add_to_cart(request, product_id, quantity=1):
    cart = get_cart(request)
    product = Product.objects.get(id=product_id)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return cart_item

def remove_from_cart(request, product_id):
    cart = get_cart(request)
    CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    
def update_cart_item(request, product_id, quantity):
    cart = get_cart(request)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass

def get_cart_items(request):
    cart = get_cart(request)
    return cart.items.select_related('product').all()

def get_cart_total(request):
    cart = get_cart(request)
    return cart.total_price

def clear_cart(request):
    cart = get_cart(request)
    cart.items.all().delete()
    request.session.pop('cart_id', None)