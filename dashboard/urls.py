from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('sales/', views.dashboard_sales, name='dashboard_sales'),
    path('products/', views.dashboard_products, name='dashboard_products'),
    path('users/', views.dashboard_users, name='dashboard_users'),
    path('finance/', views.dashboard_finance, name='dashboard_finance'),
    path('reports/', views.dashboard_reports, name='dashboard_reports'),
    
    # API endpoints
    path('api/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/report/<str:report_id>/', views.api_generate_report, name='api_generate_report'),

    path('manage-products/', views.manage_products, name='manage_products'),
    
    # API для управления продуктами
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('api/toggle-product-status/<int:product_id>/', views.api_toggle_product_status, name='api_toggle_product_status'),
    path('api/bulk-product-action/', views.api_bulk_product_action, name='api_bulk_product_action'),
    path('api/delete-product/<int:product_id>/', views.api_delete_product, name='api_delete_product'),
    
    # API для управления категориями
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/categories/<int:category_id>/', views.api_category_detail, name='api_category_detail'),
    path('api/toggle-category-status/<int:category_id>/', views.api_toggle_category_status, name='api_toggle_category_status'),
    path('api/delete-category/<int:category_id>/', views.api_delete_category, name='api_delete_category'),
    
    # Импорт/Экспорт
    path('api/import-products/', views.api_import_products, name='api_import_products'),
    path('api/export-products/', views.api_export_products, name='api_export_products'),
]