from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task(bind=True, max_retries=3)
def check_website_task(self, website_id):
    """Celery task to check a single website."""
    try:
        from monitors.models import Website
        from monitors.checker import run_check_for_website
        website = Website.objects.get(id=website_id, is_active=True)
        run_check_for_website(website)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def check_all_websites():
    """Celery beat task: check all active websites."""
    from monitors.models import Website
    from monitors.checker import run_check_for_website

    now = timezone.now()
    websites = Website.objects.filter(is_active=True)
    for website in websites:
        if website.last_checked is None or \
           now - website.last_checked >= timedelta(minutes=website.check_interval):
            check_website_task.delay(website.id)


@shared_task
def cleanup_old_checks():
    """Remove check records older than 30 days."""
    from monitors.models import MonitorCheck
    cutoff = timezone.now() - timedelta(days=30)
    deleted, _ = MonitorCheck.objects.filter(checked_at__lt=cutoff).delete()
    return f"Deleted {deleted} old check records"
