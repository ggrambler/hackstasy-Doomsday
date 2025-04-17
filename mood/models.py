from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        ('Very Happy', 'Very Happy'),
        ('Happy', 'Happy'),
        ('Neutral', 'Neutral'),
        ('Sad', 'Sad'),
        ('Very Sad', 'Very Sad'),
    ]
    
    ACTIVITY_CHOICES = [
        ('Work', 'Work'),
        ('Family', 'Family'),
        ('Friends', 'Friends'),
        ('Exercise', 'Exercise'),
        ('Hobbies', 'Hobbies'),
        ('Rest', 'Rest'),
        ('Other', 'Other'),
    ]

    SLEEP_CHOICES = [
        ('0-4', 'Less than 4 hours'),
        ('4-6', '4-6 hours'),
        ('6-8', '6-8 hours'),
        ('8+', 'More than 8 hours'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_entries')
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES)
    note = models.TextField(max_length=500, blank=True)
    date = models.DateTimeField()
    local_timezone = models.CharField(max_length=50, default=timezone.get_current_timezone_name)
    intensity = models.IntegerField(default=3)  # Scale of 1-5
    
    # New fields
    activities = models.CharField(max_length=50, choices=ACTIVITY_CHOICES, default='Other')
    sleep_hours = models.CharField(max_length=10, choices=SLEEP_CHOICES, default='6-8')
    energy_level = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])  # 1-5 scale
    stress_level = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])  # 1-5 scale
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Mood entries'

    def __str__(self):
        return f"{self.user.username}'s mood on {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Set intensity based on mood
        mood_to_intensity = {
            'Very Happy': 5,
            'Happy': 4,
            'Neutral': 3,
            'Sad': 2,
            'Very Sad': 1
        }
        self.intensity = mood_to_intensity.get(self.mood, 3)
        super().save(*args, **kwargs)

    @classmethod
    def get_user_insights(cls, user):
        """Get mood insights for the user"""
        entries = cls.objects.filter(user=user)
        total_entries = entries.count()
        
        if total_entries == 0:
            return None

        # Calculate averages
        avg_mood = entries.aggregate(Avg('intensity'))['intensity__avg']
        avg_energy = entries.aggregate(Avg('energy_level'))['energy_level__avg']
        avg_stress = entries.aggregate(Avg('stress_level'))['stress_level__avg']

        # Get most common activities during good moods (intensity > 3)
        good_mood_activities = (
            entries.filter(intensity__gt=3)
            .values('activities')
            .annotate(count=models.Count('id'))
            .order_by('-count')
        )

        # Get most common activities during bad moods (intensity < 3)
        bad_mood_activities = (
            entries.filter(intensity__lt=3)
            .values('activities')
            .annotate(count=models.Count('id'))
            .order_by('-count')
        )

        # Sleep pattern analysis
        sleep_mood_correlation = {}
        for sleep_choice in cls.SLEEP_CHOICES:
            sleep_entries = entries.filter(sleep_hours=sleep_choice[0])
            if sleep_entries.exists():
                avg_mood_for_sleep = sleep_entries.aggregate(Avg('intensity'))['intensity__avg']
                sleep_mood_correlation[sleep_choice[1]] = avg_mood_for_sleep

        return {
            'total_entries': total_entries,
            'avg_mood': round(avg_mood, 2) if avg_mood else None,
            'avg_energy': round(avg_energy, 2) if avg_energy else None,
            'avg_stress': round(avg_stress, 2) if avg_stress else None,
            'good_mood_activities': list(good_mood_activities[:3]),
            'bad_mood_activities': list(bad_mood_activities[:3]),
            'sleep_mood_correlation': sleep_mood_correlation
        }
