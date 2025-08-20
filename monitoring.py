# monitoring.py - Basic monitoring setup
import logging
import time
from django.core.management.base import BaseCommand
from django.db import connection
from webhooks.models import WebhookEvent
from accounts.models import FacebookPage

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Monitor application health and webhook activity'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')

    def handle(self, *args, **options):
        interval = options['interval']
        self.stdout.write(f'Starting monitoring with {interval}s interval...')

        while True:
            try:
                self.check_database_health()
                self.check_webhook_activity()
                self.check_facebook_tokens()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write('Monitoring stopped.')
                break
            except Exception as e:
                logger.error(f'Monitoring error: {e}')
                time.sleep(interval)

    def check_database_health(self):
        """Check database connectivity"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            logger.info("Database: Healthy")
        except Exception as e:
            logger.error(f"Database: Unhealthy - {e}")

    def check_webhook_activity(self):
        """Check recent webhook activity"""
        from django.utils import timezone
        from datetime import timedelta

        recent_events = WebhookEvent.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).count()
        
        logger.info(f"Webhook Events (last 5min): {recent_events}")

    def check_facebook_tokens(self):
        """Check for expiring Facebook tokens"""
        from django.utils import timezone
        from datetime import timedelta

        expiring_soon = FacebookPage.objects.filter(
            facebook_user__token_expires_at__lte=timezone.now() + timedelta(days=7),
            facebook_user__token_expires_at__isnull=False
        ).count()

        if expiring_soon > 0:
            logger.warning(f"Facebook tokens expiring soon: {expiring_soon}")
