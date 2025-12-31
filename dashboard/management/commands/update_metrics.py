# dashboard/management/commands/update_metrics.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.utils import calculate_daily_metrics
from datetime import timedelta

class Command(BaseCommand):
    help = 'Обновляет метрики дашборда'
    
    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=1, help='Количество дней для обработки')
    
    def handle(self, *args, **options):
        days = options['days']
        
        for i in range(days):
            date = timezone.now().date() - timedelta(days=i)
            metrics = calculate_daily_metrics(date)
            
            self.stdout.write(
                self.style.SUCCESS(f'Метрики за {date} обновлены: '
                                   f'{metrics.total_orders} заказов, '
                                   f'{metrics.total_revenue} руб.')
            )