from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'websites', views.WebsiteViewSet)
router.register(r'checks', views.MonitorCheckViewSet)
router.register(r'incidents', views.IncidentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
