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
        }

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['workout', 'start_time', 'end_time']
        widgets = {
            'workout': forms.Select(),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time.date() != end_time.date():
            print("time", start_time.date(), end_time.date())
            raise ValidationError(
                    "Start time and end time must be on the same day"
                )
        if start_time and end_time and end_time < start_time:
            raise ValidationError(
                    "End time cannot be before start time"
                )
        if start_time and end_time and start_time == end_time:
            raise ValidationError(
                    "Start time and end time cannot be the same"
                )
        if Plan.objects.filter(
            user=self.instance.user,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError(
                    "This plan overlaps with an existing plan"
                )
        return cleaned_data


# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name',
#                   'email', 'phone', 'main_contact', 'address']
#         widgets = {
#             'address': forms.Textarea(attrs={'rows': 3}),
#         }
#     def clean_username(self):
#         data = self.cleaned_data["username"]
#         if User.objects.filter(username=data).exclude(pk=self.instance.pk).exists():
#             raise ValidationError("ชื่อนี้มีคนใช้แล้ว")
#         return data
#     def clean_email(self):
#         data = self.cleaned_data["email"]
#         if User.objects.filter(email=data).exclude(pk=self.instance.pk).exists():
#             raise ValidationError("อีเมลนี้มีคนใช้แล้ว")
#         return data
#     def clean_phone(self):
#         data = self.cleaned_data.get("phone")
#         if not data.isdigit():
#             raise ValidationError("เบอร์โทรศัพท์ต้องเป็นตัวเลขเท่านั้น")
#         return data
