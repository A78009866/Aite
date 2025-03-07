from django.shortcuts import render, redirect
from .models import Message
from django.contrib.auth.decorators import login_required

@login_required
def chat_view(request):
    if request.method == "POST":
        message_text = request.POST.get('message')
        if message_text:
            Message.objects.create(user=request.user, text=message_text)

    messages = Message.objects.all()
    return render(request, 'chatapp/chat.html', {'messages': messages})
