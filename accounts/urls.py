# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('auth/facebook/', views.facebook_login, name='facebook_login'),
    path('pages/', views.get_user_pages, name='get_user_pages'),
    path('pages/subscribe-webhooks/', views.subscribe_webhooks, name='subscribe_webhooks'),
    path('auth/logout/', views.logout_view, name='logout'),
]