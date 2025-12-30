from django.contrib import admin
from .models import Category, Product, ProductFeature


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'current_price', 'is_active', 'is_featured', 'sales_count', 'created_at')
    list_filter = ('is_active', 'is_featured', 'category', 'product_type', 'created_at')
    search_fields = ('name', 'description', 'tags')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_featured')
    inlines = [ProductFeatureInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'name', 'slug', 'short_description', 'description', 'detailed_description')
        }),
        ('Цены', {
            'fields': ('price', 'discount_price')
        }),
        ('Файлы и изображения', {
            'fields': ('file', 'preview_image', 'additional_images')
        }),
        ('Техническая информация', {
            'fields': ('product_type', 'tags', 'file_size', 'file_format', 'version', 'compatibility')
        }),
        ('Статистика', {
            'fields': ('is_active', 'is_featured', 'sales_count', 'view_count')
        }),
    )