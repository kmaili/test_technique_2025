from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
    path('api/measurements/latest/', views.latest_measurements, name='latest_measurements'),
    path('api/measurements/', views.measurements_list, name='measurements_list'),
    path('', views.realtime_view, name='realtime'),
]
