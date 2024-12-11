from django.urls import path 
from . import views

app_name='chatbot'
urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('delete-all-chats', views.delete_all_chats, name='delete_all_chats'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
]
