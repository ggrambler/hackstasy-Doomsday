from django.contrib import admin
from .models import MoodEntry

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood', 'note', 'date')
    list_filter = ('mood', 'date', 'user')
    search_fields = ('user__username', 'mood', 'note')
    date_hierarchy = 'date'
