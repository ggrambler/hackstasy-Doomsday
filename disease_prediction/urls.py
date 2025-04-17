from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict_disease, name='predict_disease'),  # Default route for disease prediction
    path('disease_info/', views.disease_info, name='disease_info'),  # Route for disease information
]
