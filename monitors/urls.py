from django.urls import path
from . import views

app_name = 'monitors'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('websites/add/', views.website_add, name='website_add'),
    path('websites/<int:pk>/', views.website_detail, name='website_detail'),
    path('websites/<int:pk>/edit/', views.website_edit, name='website_edit'),
    path('websites/<int:pk>/delete/', views.website_delete, name='website_delete'),
    path('websites/<int:pk>/check/', views.website_check_now, name='website_check_now'),
    path('incidents/', views.incidents_list, name='incidents'),
    path('api/status/', views.api_status, name='api_status'),
]
