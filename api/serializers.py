from rest_framework import serializers
from monitors.models import Website, MonitorCheck, Incident


class MonitorCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitorCheck
        fields = ['id', 'status', 'response_time', 'status_code', 'error_message', 'checked_at']


class WebsiteSerializer(serializers.ModelSerializer):
    recent_checks = MonitorCheckSerializer(many=True, read_only=True, source='checks')

    class Meta:
        model = Website
        fields = [
            'id', 'name', 'url', 'is_active', 'current_status',
            'uptime_percentage', 'response_time', 'last_checked',
            'check_interval', 'timeout', 'created_at', 'recent_checks',
        ]
        read_only_fields = ['current_status', 'uptime_percentage', 'response_time', 'last_checked']


class IncidentSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)

    class Meta:
        model = Incident
        fields = ['id', 'website', 'website_name', 'title', 'description',
                  'severity', 'started_at', 'resolved_at', 'is_resolved']
