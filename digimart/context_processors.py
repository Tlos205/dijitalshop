from products.models import Category, Product

def categories(request):
    return {
        'categories': Category.objects.all().order_by('name'),
        'product_types': Product.PRODUCT_TYPE_CHOICES
    }