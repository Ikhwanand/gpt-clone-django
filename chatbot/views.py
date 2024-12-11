from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
import os

from django.contrib import auth 
from django.contrib.auth.models import User 
from .models import Chat
from django.utils import timezone
from dotenv import load_dotenv
from django.contrib.auth.decorators import login_required
# Create your views here.

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("GLHF_API_KEY", ""),
    base_url="https://glhf.chat/api/openai/v1",
)

def ask_chat(message):
    response = client.chat.completions.create(
        model="hf:meta-llama/Llama-3.1-405B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ]
    )
    
    answer = response.choices[0].message.content.strip()
    return answer

@login_required(login_url='chatbot:login')
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_chat(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


@login_required(login_url='chatbot:login')
def delete_all_chats(request):
    if request.method == 'POST':
        chats = Chat.objects.filter(user=request.user)
        chats.delete()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
    


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot:chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
    

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot:chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'signup.html', {'error_message': error_message})
    return render(request, 'signup.html')


def logout(request):
    auth.logout(request)
    return redirect('chatbot:login')