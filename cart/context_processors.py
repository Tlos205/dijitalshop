from .utils import get_cart, get_cart_total

def cart(request):
    cart = get_cart(request)
    cart_total = get_cart_total(request) if cart else 0
    cart_items_count = cart.total_items if cart else 0
    
    return {
        'cart': cart,
        'cart_total': cart_total,
        'cart_items_count': cart_items_count,
    }