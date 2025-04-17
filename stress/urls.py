from django.urls import path
from . import views

urlpatterns = [
    path('', views.stress_management, name='stress_management'),
]
