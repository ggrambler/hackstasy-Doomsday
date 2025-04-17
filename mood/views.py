from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import MoodEntry
import pandas as pd
from datetime import datetime, timedelta

@login_required
def mood_tracker(request):
    try:
        # Assuming `get_user_insights` is a method that gets the insights for the user
        insights = MoodEntry.get_user_insights(request.user)
        context = {
            'insights': insights,
            'mood_entry': MoodEntry,  # Pass the model class to access choices
        }
        return render(request, 'mood/mood_tracker.html', context)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def add_mood(request):
    if request.method == 'POST':
        try:
            mood = request.POST.get('mood')
            if not mood or mood not in dict(MoodEntry.MOOD_CHOICES):
                return JsonResponse({'status': 'error', 'message': 'Invalid or missing mood value'}, status=400)

            activities = request.POST.get('activities', 'Other')
            if activities not in dict(MoodEntry.ACTIVITY_CHOICES):
                activities = 'Other'

            sleep_hours = request.POST.get('sleep_hours', '6-8')
            if sleep_hours not in dict(MoodEntry.SLEEP_CHOICES):
                sleep_hours = '6-8'

            energy_level = int(request.POST.get('energy_level', 3))
            if not 1 <= energy_level <= 5:
                energy_level = 3

            stress_level = int(request.POST.get('stress_level', 3))
            if not 1 <= stress_level <= 5:
                stress_level = 3

            current_time = timezone.now()

            mood_entry = MoodEntry.objects.create(
                user=request.user,
                mood=mood,
                note=request.POST.get('note', ''),
                activities=activities,
                sleep_hours=sleep_hours,
                energy_level=energy_level,
                stress_level=stress_level,
                location=request.POST.get('location', ''),
                date=current_time
            )

            response_data = {
                'id': mood_entry.id,
                'date': current_time.strftime("%Y-%m-%d %H:%M"),
                'mood': mood_entry.mood,
                'note': mood_entry.note,
                'activities': mood_entry.activities,
                'sleep_hours': mood_entry.sleep_hours,
                'energy_level': mood_entry.energy_level,
                'stress_level': mood_entry.stress_level,
                'location': mood_entry.location,
            }

            return JsonResponse({'status': 'success', 'data': response_data})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while saving your mood: ' + str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def get_mood_data(request):
    try:
        time_range = request.GET.get('range', 'all')
        if time_range == 'week':
            start_date = timezone.now() - timedelta(days=7)
        elif time_range == 'month':
            start_date = timezone.now() - timedelta(days=30)
        else:
            start_date = None

        entries = MoodEntry.objects.filter(user=request.user)
        if start_date:
            entries = entries.filter(date__gte=start_date)

        entries = entries.order_by('-date')
        mood_data = [{
            'id': entry.id,
            'date': entry.date.strftime("%Y-%m-%d %H:%M"),
            'mood': entry.mood,
            'note': entry.note,
            'activities': entry.activities,
            'sleep_hours': entry.sleep_hours,
            'energy_level': entry.energy_level,
            'stress_level': entry.stress_level,
            'location': entry.location,
        } for entry in entries]
        return JsonResponse(mood_data, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Failed to fetch mood data: ' + str(e)}, status=500)

@login_required
def export_data(request):
    try:
        entries = MoodEntry.objects.filter(user=request.user).order_by('-date')
        format_type = request.GET.get('format', 'csv')

        if not entries.exists():
            return JsonResponse({'status': 'error', 'message': 'No mood data available to export'}, status=404)

        data = [{
            'Date': entry.date.strftime("%Y-%m-%d"),
            'Time': entry.date.strftime("%H:%M"),
            'Mood': entry.mood,
            'Activities': entry.activities,
            'Sleep Hours': entry.sleep_hours,
            'Energy Level': entry.energy_level,
            'Stress Level': entry.stress_level,
            'Location': entry.location,
            'Note': entry.note
        } for entry in entries]

        df = pd.DataFrame(data)

        if format_type == 'excel':
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=mood_data.xlsx'
            df.to_excel(response, index=False, engine='openpyxl')
        else:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=mood_data.csv'
            df.to_csv(response, index=False)

        return response
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Failed to export mood data: ' + str(e)}, status=500)
