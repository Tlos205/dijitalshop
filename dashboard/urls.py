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
    
     path('manage-products/', views.manage_products, name='manage_products'),
    
    # API для товаров
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/create/', views.api_create_product, name='api_create_product'),
    path('api/products/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('api/products/<int:product_id>/update/', views.api_update_product, name='api_update_product'),
    path('api/products/<int:product_id>/toggle-status/', views.api_toggle_product_status, name='api_toggle_product_status'),
    path('api/products/<int:product_id>/toggle-featured/', views.api_toggle_featured, name='api_toggle_featured'),
    path('api/products/<int:product_id>/delete/', views.api_delete_product, name='api_delete_product'),
    path('api/products/bulk-action/', views.api_bulk_product_action, name='api_bulk_product_action'),
    path('api/products/<int:product_id>/set-discount/', views.api_set_discount, name='api_set_discount'),
    path('api/products/<int:product_id>/remove-discount/', views.api_remove_discount, name='api_remove_discount'),
    path('api/products/<int:product_id>/duplicate/', views.api_duplicate_product, name='api_duplicate_product'),
    
    # API для категорий
    path('api/categories/', views.api_categories_list, name='api_categories_list'),
    path('api/categories/create/', views.api_create_category, name='api_create_category'),
    path('api/categories/<int:category_id>/', views.api_category_detail, name='api_category_detail'),
    path('api/categories/<int:category_id>/update/', views.api_update_category, name='api_update_category'),
    path('api/categories/<int:category_id>/toggle-status/', views.api_toggle_category_status, name='api_toggle_category_status'),
    path('api/categories/<int:category_id>/delete/', views.api_delete_category, name='api_delete_category'),
    
    # Импорт/экспорт
    path('api/import-products/', views.api_import_products, name='api_import_products'),
    path('api/export-products/', views.api_export_products, name='api_export_products'),
    
    # Дополнительные API
    path('api/product-types/', views.api_get_product_types, name='api_get_product_types'),
]