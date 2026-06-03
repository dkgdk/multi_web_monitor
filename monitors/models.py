from django.db import models
from django.utils import timezone


class Website(models.Model):
    STATUS_CHOICES = [
        ('up', 'Up'),
        ('down', 'Down'),
        ('unknown', 'Unknown'),
    ]

    name = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True)
    check_interval = models.PositiveIntegerField(default=5, help_text="Check interval in minutes")
    timeout = models.PositiveIntegerField(default=30, help_text="Timeout in seconds")
    notify_email = models.EmailField(blank=True, null=True)
    current_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    last_checked = models.DateTimeField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in ms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uptime_percentage = models.FloatField(default=0.0)
    total_checks = models.PositiveIntegerField(default=0)
    successful_checks = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Website'
        verbose_name_plural = 'Websites'

    def __str__(self):
        return f"{self.name} ({self.url})"

    def update_uptime(self):
        if self.total_checks > 0:
            self.uptime_percentage = round((self.successful_checks / self.total_checks) * 100, 2)
        else:
            self.uptime_percentage = 0.0

    @property
    def status_color(self):
        colors = {'up': 'success', 'down': 'danger', 'unknown': 'warning'}
        return colors.get(self.current_status, 'secondary')

    @property
    def status_icon(self):
        icons = {'up': '✓', 'down': '✗', 'unknown': '?'}
        return icons.get(self.current_status, '?')


class MonitorCheck(models.Model):
    STATUS_CHOICES = [
        ('up', 'Up'),
        ('down', 'Down'),
        ('error', 'Error'),
    ]

    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='checks')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in ms")
    status_code = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    checked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-checked_at']
        verbose_name = 'Monitor Check'
        verbose_name_plural = 'Monitor Checks'

    def __str__(self):
        return f"{self.website.name} - {self.status} @ {self.checked_at:%Y-%m-%d %H:%M}"


class Incident(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]

    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='incidents')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='critical')
    started_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'

    def __str__(self):
        return f"{self.website.name} - {self.title}"

    @property
    def duration(self):
        end = self.resolved_at or timezone.now()
        delta = end - self.started_at
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
