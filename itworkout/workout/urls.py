from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name='register'),
    path("home/", views.CalendarView.as_view(), name="home"),
    path("profile/", views.ProfileEdit.as_view(), name='profile'),
    path('trainers/', views.TrainersList.as_view(), name='trainers'),
    path('chat/', views.ChatList.as_view(), name='chat_list'),
    path('chat/<int:trainer_id>/', views.ChatStart.as_view(), name='chat_start'),
    path('chat/room/<int:room_id>/', views.ChatRoomView.as_view(), name='chat_room'),
    path('chat/messages/<int:room_id>/', views.ChatMessagesView.as_view(), name='chat_messages'),
    path('chat/updates/', views.ChatUpdatesView.as_view(), name='chat_updates'),
    path('chat/delete/<int:room_id>/', views.chat_delete, name='chat_delete'),
    path("calendar/", views.CalendarView.as_view(), name='calendar'),
    path("addplan/", views.AddPlanView.as_view(), name='addplan'),
    path("editplan/<int:plan_id>/", views.EditPlanView.as_view(), name='editplan'),
    path("deleteplan/<int:plan_id>/", views.DeletePlanView.as_view(), name='deleteplan'),
    path("calculate/", views.CalculateView.as_view(), name='calculate'),
    path("history/", views.HistoryView.as_view(), name='history'),
]
# test change
