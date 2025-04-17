from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('chat/', include('chat.urls')),
    path('record_bp/', views.record_bp, name='record_bp'),
    path('view_bp/', views.view_bp, name='view_bp'),
    path('daily_journal/', views.daily_journal, name='daily_journal'),
    path('get_journal_entry/', views.get_journal_entry, name='get_journal_entry'),
]
