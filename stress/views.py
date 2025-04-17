from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from django.http import JsonResponse

@login_required
def stress_management(request):
    # Get list of meditation audio files
    media_dir = os.path.join(settings.MEDIA_ROOT)
    audio_files = []
    
    if os.path.exists(media_dir):
        for file in os.listdir(media_dir):
            if file.endswith('.mp3'):
                audio_files.append({
                    'name': file.replace('-', ' ').replace('.mp3', ''),
                    'url': f'/media/{file}'
                })
    
    context = {
        'audio_files': audio_files,
        'breathing_exercises': [
            {
                'name': 'Box Breathing',
                'description': 'Inhale for 4 counts, hold for 4, exhale for 4, hold for 4.',
                'duration': '5 minutes'
            },
            {
                'name': '4-7-8 Breathing',
                'description': 'Inhale for 4 counts, hold for 7, exhale for 8.',
                'duration': '5 minutes'
            },
            {
                'name': 'Deep Breathing',
                'description': 'Slow, deep breaths focusing on filling and emptying the lungs completely.',
                'duration': '3 minutes'
            }
        ],
        'meditation_tips': [
            'Find a quiet, comfortable space',
            'Start with short sessions (5-10 minutes)',
            'Focus on your breath',
            'Let thoughts pass without judgment',
            'Practice regularly for best results'
        ]
    }
    
    return render(request, 'stress/stress_management.html', context)
