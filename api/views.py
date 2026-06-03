from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from monitors.models import Website, MonitorCheck, Incident
from monitors.checker import run_check_for_website
from .serializers import WebsiteSerializer, MonitorCheckSerializer, IncidentSerializer


class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    @action(detail=True, methods=['post'])
    def check(self, request, pk=None):
        website = self.get_object()
        check = run_check_for_website(website)
        return Response(MonitorCheckSerializer(check).data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        website = self.get_object()
        checks = website.checks.all()[:100]
        return Response(MonitorCheckSerializer(checks, many=True).data)


class MonitorCheckViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonitorCheck.objects.all().select_related('website')
    serializer_class = MonitorCheckSerializer


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects.all().select_related('website')
    serializer_class = IncidentSerializer
