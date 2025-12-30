# products/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Product, Category

class HomeView(ListView):
    model = Product
    template_name = 'products/home.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.filter(
            is_active=True
        ).select_related('category').order_by('-created_at')[:8]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['featured_products'] = Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).order_by('-sales_count')[:4]
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Увеличиваем счетчик просмотров
        product.view_count += 1
        product.save(update_fields=['view_count'])
        
        # Рекомендуемые товары
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        return context

class CategoryDetailView(ListView):
    model = Product
    template_name = 'products/category_detail.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        queryset = Product.objects.filter(
            category=self.category,
            is_active=True
        ).select_related('category')
        
        # Фильтрация по типу товара
        product_type = self.request.GET.get('type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        # Сортировка
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-sales_count')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['product_types'] = Product.TYPE_CHOICES
        return context

class SearchView(ListView):
    model = Product
    template_name = 'products/search.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query) |
                Q(short_description__icontains=query),
                is_active=True
            ).select_related('category').order_by('-created_at')
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['results_count'] = self.get_queryset().count()
        return context

def all_products(request):
    products = Product.objects.filter(is_active=True)
    
    # Фильтрация
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    product_type = request.GET.get('product_type')
    if product_type:
        products = products.filter(product_type=product_type)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-sales_count')
    else:
        products = products.order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'product_types': Product.TYPE_CHOICES,
    }
    
    return render(request, 'products/all_products.html', context)