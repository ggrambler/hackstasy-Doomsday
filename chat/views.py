from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Message
import json

@login_required
def group_chat(request):
    return render(request, 'chat/group_chat.html')

@login_required
def fetch_messages(request):
    messages = Message.objects.all().values('id', 'sender__username', 'content', 'timestamp')
    return JsonResponse(list(messages), safe=False)

@csrf_exempt
@login_required
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get('content')
        sender = request.user
        if content:
            message = Message.objects.create(sender=sender, content=content)
            return JsonResponse({'id': message.id, 'sender': sender.username, 'content': content, 'timestamp': message.timestamp}, status=201)
        return JsonResponse({'error': 'Empty message'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=405)
