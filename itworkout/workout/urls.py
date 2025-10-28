from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name='register'),
    path("home/", views.HomeView.as_view(), name="home"),
    path("profile/", views.ProfileEdit.as_view(), name='profile'),
]
# test change