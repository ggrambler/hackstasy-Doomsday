from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm,BPRecordForm
from django.contrib.auth.models import User
from .models import Profile, BPRecord
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.http import JsonResponse
from .models import JournalEntry
from datetime import date

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # Get user's mood statistics
    mood_entries = request.user.mood_entries.all()
    total_entries = mood_entries.count()
    mood_distribution = {}
    if total_entries > 0:
        for mood_choice, _ in request.user.mood_entries.model.MOOD_CHOICES:
            count = mood_entries.filter(mood=mood_choice).count()
            percentage = (count / total_entries) * 100
            mood_distribution[mood_choice] = {
                'count': count,
                'percentage': round(percentage, 1)
            }

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'mood_stats': {
            'total_entries': total_entries,
            'mood_distribution': mood_distribution
        }
    }
    return render(request, 'accounts/profile.html', context)

def index(request):
    return render(request, 'index.html')




@login_required
def record_bp(request):
    if request.method == "POST":
        form = BPRecordForm(request.POST)
        if form.is_valid():
            bp_record = form.save(commit=False)
            bp_record.user = request.user
            bp_record.save()
            return redirect('view_bp')
    else:
        form = BPRecordForm()
    return render(request, 'accounts/record_bp.html', {'form': form})

@login_required
def view_bp(request):
    bp_records = BPRecord.objects.filter(user=request.user).order_by('date')

    # Prepare data for the graph
    dates = [record.date for record in bp_records]
    systolic = [record.systolic for record in bp_records]
    diastolic = [record.diastolic for record in bp_records]

    # Generate graph
    plt.figure(figsize=(10, 6))
    plt.plot(dates, systolic, label="Systolic Pressure", marker='o')
    plt.plot(dates, diastolic, label="Diastolic Pressure", marker='o')
    plt.title("Blood Pressure Over Time")
    plt.xlabel("Date")
    plt.ylabel("Pressure (mmHg)")
    plt.legend()
    plt.grid()

    # Convert graph to PNG image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graph = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'accounts/view_bp.html', {'bp_records': bp_records, 'graph': graph})

@login_required
def daily_journal(request):
    if request.method == 'POST':
        journal_date = request.POST.get('date', date.today())
        content = request.POST.get('content', '')
        JournalEntry.objects.update_or_create(
            user=request.user,
            date=journal_date,
            defaults={'content': content}
        )
        return JsonResponse({'status': 'success', 'message': 'Journal entry saved!'})
    return render(request, 'daily_journal.html')

@login_required
def get_journal_entry(request):
    journal_date = request.GET.get('date', date.today())
    try:
        entry = JournalEntry.objects.get(user=request.user, date=journal_date)
        return JsonResponse({'status': 'success', 'content': entry.content})
    except JournalEntry.DoesNotExist:
        return JsonResponse({'status': 'success', 'content': ''})

@login_required
def daily_journal(request):
    if request.method == 'POST':
        journal_date = request.POST.get('date', date.today())
        content = request.POST.get('content', '')
        JournalEntry.objects.update_or_create(
            user=request.user,
            date=journal_date,
            defaults={'content': content}
        )
        return JsonResponse({'status': 'success', 'message': 'Journal entry saved!'})

    # Fetch all journal entries for the logged-in user
    entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
    return render(request, 'daily_journal.html', {'entries': entries})

