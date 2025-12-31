# dashboard/admin.py
from django.contrib import admin
from .models import DashboardMetric, VisitorLog, SaleAnalytics

@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_revenue', 'total_orders', 'new_users')
    list_filter = ('date',)
    search_fields = ('date',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'page_url', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'page_url', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(SaleAnalytics)
class SaleAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'total_sales', 'total_revenue')
    list_filter = ('date', 'category')
    search_fields = ('category__name',)
    date_hierarchy = 'date'