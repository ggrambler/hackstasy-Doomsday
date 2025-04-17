from django.urls import path
from . import views

urlpatterns = [
    path('', views.mood_tracker, name='mood_tracker'),  # Main mood tracker page
    path('add/', views.add_mood, name='add_mood'),  # Add mood entry
    path('data/', views.get_mood_data, name='get_mood_data'),  # Retrieve mood data
    path('export/', views.export_data, name='export_mood_data'),  # Export mood data (CSV/Excel)
]
