# webhooks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('facebook/', views.facebook_webhook, name='facebook_webhook'),
    path('events/', views.get_webhook_events, name='get_webhook_events'),
]