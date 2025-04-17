from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_chat, name='group_chat'),
    path('fetch_messages/', views.fetch_messages, name='fetch_messages'),
    path('send_message/', views.send_message, name='send_message'),
]
