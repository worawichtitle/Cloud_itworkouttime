from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name='register'),
    path("home/", views.HomeView.as_view(), name="home"),
    path("profile/", views.ProfileEdit.as_view(), name='profile'),
    path('trainers/', views.TrainersList.as_view(), name='trainers'),
    path('chat/', views.ChatList.as_view(), name='chat_list'),
    path('chat/<int:trainer_id>/', views.ChatStart.as_view(), name='chat_start'),
    path('chat/room/<int:room_id>/', views.ChatRoomView.as_view(), name='chat_room'),
    path('chat/messages/<int:room_id>/', views.ChatMessagesView.as_view(), name='chat_messages'),
    path('chat/updates/', views.ChatUpdatesView.as_view(), name='chat_updates'),
    path('chat/mark_read/<int:room_id>/', views.chat_mark_read, name='chat_mark_read'),
]