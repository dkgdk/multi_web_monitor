from django.contrib import admin
from django.utils.html import format_html
from .models import Website, MonitorCheck, Incident


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'status_badge', 'uptime_percentage', 'response_time', 'last_checked', 'is_active']
    list_filter = ['current_status', 'is_active']
    search_fields = ['name', 'url']
    readonly_fields = ['current_status', 'last_checked', 'response_time', 'uptime_percentage', 'total_checks', 'successful_checks']
    list_per_page = 25

    def status_badge(self, obj):
        colors = {'up': '#22c55e', 'down': '#ef4444', 'unknown': '#f59e0b'}
        color = colors.get(obj.current_status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;border-radius:12px;font-size:12px;">{}</span>',
            color, obj.current_status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(MonitorCheck)
class MonitorCheckAdmin(admin.ModelAdmin):
    list_display = ['website', 'status', 'status_code', 'response_time', 'checked_at']
    list_filter = ['status', 'website']
    search_fields = ['website__name']
    readonly_fields = ['website', 'status', 'response_time', 'status_code', 'error_message', 'checked_at']
    list_per_page = 50


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['website', 'title', 'severity', 'started_at', 'is_resolved', 'resolved_at']
    list_filter = ['severity', 'is_resolved', 'website']
    search_fields = ['website__name', 'title']
    list_per_page = 25
