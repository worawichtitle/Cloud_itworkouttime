from django.forms import ModelForm
from .models import *
from django.core.exceptions import ValidationError
from django.forms.widgets import Textarea, RadioSelect, TimeInput, FileInput
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as Authen

class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    class Meta:
        model = Authen
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = Authen
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm'}),
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm'}),
        }

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['tel', 'user_image']  # remove role from form fields
        widgets = {
            "user_image": FileInput(attrs={"class": "block w-full text-sm text-gray-500", "accept": "image/*"}),
            "tel": forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm'}),
        }