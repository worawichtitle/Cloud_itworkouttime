
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.views import View
from workout.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta, date
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login
from workout.forms import *
from django.db.models import Q
from django.db import transaction
# Create your views here.


def calendar_view(request):
    activities = Plan.objects.filter(user=request.user)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = [f"{h:02d}:00" for h in range(0, 15)]  # 00:00–14:00

    context = {
        'activities': activities,
        'days': days,
        'hours': hours,
    }
    return render(request, 'workout/calendar.html', context)
