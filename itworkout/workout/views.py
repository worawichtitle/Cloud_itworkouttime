from django.shortcuts import render, redirect
from django.views import View
from workout.models import *
from django.shortcuts import render, redirect, get_object_or_404
from workout.forms import *
from workout.utils.week import get_week_dates, get_duration_minutes

from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from datetime import datetime, timedelta, date

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'logins/login.html', {"form": form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        next_path = request.GET.get("next", 'calendar')
        if form.is_valid():
            user = form.get_user() 
            login(request,user)
            return redirect(next_path)

        return render(request,'logins/login.html', {"form":form})

class LogoutView(View): 
    def get(self, request):
        logout(request)
        return redirect('login')

class RegisterView(View):
    def get(self, request):
        user = UserCreationForm()
        customer = UserForm()
        form = {
            "user" : user,
            "customer" : customer,
        }
        return render(request, 'logins/register.html', {'form': form})
    
    def post(self, request):
        user = UserCreationForm(request.POST)
        # accept uploaded files for customer (profile image)
        customer = UserForm(request.POST)
        form = {
            "user" : user,
            "customer" : customer,
        }
        try:
            with transaction.atomic():
                if user.is_valid():
                    us = user.save()
                    if customer.is_valid():
                        cus = customer.save(commit=False)
                        cus.authen = us
                        cus.role = 'user'
                        cus.save()
                        # default_group = Group.objects.get(name='Customer')
                        # us.groups.add(default_group)
                        login(request, us)

                        return redirect('calendar')
                    else:
                        # หากฟอร์ม Customer ไม่ถูกต้อง
                        return render(request, 'logins/register.html', {"form": form, "error": "กรุณากรอกข้อมูลลูกค้าให้ครบถ้วน"})
                else:
                    # หากฟอร์ม User ไม่ถูกต้อง
                    return render(request, 'logins/register.html', {"form": form, "error": "กรุณากรอกข้อมูลผู้ใช้ให้ครบถ้วน"})
        except Exception as e:
            # ถ้ามีข้อผิดพลาดในการสมัครสมาชิก, ให้ render หน้าเดิมและส่งกลับ error message
            print(f"Error: {str(e)}")
            return render(request, 'logins/register.html', {"form": form})
        
class HomeView(View): 
    def get(self, request):
        return render(request, 'base.html')
    
class ProfileEdit(LoginRequiredMixin, View):
    def get(self, request):
        try:
            profile = request.user.user
            user_form = UserEditForm(instance=request.user)
            profile_form = UserForm(instance=profile)
            context = {
                'user_form': user_form,
                'profile_form': profile_form
            }
            return render(request, 'homes/profile.html', context)
        except User.DoesNotExist:
            return redirect('calendar')

    def post(self, request):
        try:
            profile = request.user.user
            user_form = UserEditForm(request.POST, instance=request.user)
            profile_form = UserForm(request.POST, request.FILES, instance=profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                profile = profile_form.save(commit=False)
                
                # Update role based on checkbox
                is_trainer = request.POST.get('is_trainer')
                profile.role = 'trainer' if is_trainer else 'user'
                
                profile.save()
                return redirect('calendar')
            
            context = {
                'user_form': user_form,
                'profile_form': profile_form
            }
            return render(request, 'homes/profile.html', context)
        except User.DoesNotExist:
            return redirect('calendar')
        

class CalendarView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.user
        print("Profile: ", profile, profile.tel)
        offset = int(request.GET.get('week_offset', 0))
        reference_date = datetime.today() + timedelta(weeks=offset)

        week_dates = get_week_dates(reference_date)
        start_range = week_dates[0].date()
        end_range = week_dates[-1].date()

        plans = Plan.objects.filter(
            user=profile,
            start_time__date__range=(start_range, end_range)
        )
        print(plans)
        enriched_plans = []
        for plan in plans:
            duration = get_duration_minutes(plan.start_time, plan.end_time)
            print("Duration:", duration)
            print("hour", plan.start_time.hour, "minute:", plan.start_time.minute)
            enriched_plans.append({
                'id': plan.id,
                'workout': plan.workout,
                'day': plan.day,  # 0 = Monday
                'start_time': plan.start_time,
                'end_time': plan.end_time,
                'start_minute': plan.start_time.minute,
                # 'left_px': plan.start_hour * 60 + plan.start_minute,
                'left_px': plan.start_time.minute * (100 / 60),
                'width_px': duration * (100 / 60),
            })


        # days = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
        hours = [f"{h:02d}:00" for h in range(0, 24)]  # 00:00–24:00

        context = {
            'plans': enriched_plans,
            # 'days': days,
            'offset': offset,
            'hours': hours,
            'week_dates': week_dates,
            'week_range': f"{week_dates[0].strftime('%d %b')} - {week_dates[-1].strftime('%d %b %Y')}",
        }
        return render(request, 'calendar/calendar.html', context)


class AddPlanView(LoginRequiredMixin, View):
    def get(self, request):
        form = PlanForm()
        context = {
            'form': form,
        }
        return render(request, 'calendar/addcalendar.html', context)

    def post(self, request):
        profile = request.user.user
        form = PlanForm(request.POST, instance=Plan(user=profile))
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = profile
            plan.day = plan.start_time.weekday()
            plan.save()
            return redirect('calendar')
        context = {
            'form': form,
        }
        return render(request, 'calendar/addcalendar.html', context)
    

class EditPlanView(LoginRequiredMixin, View):
    def get(self, request, plan_id):
        profile = request.user.user
        try:
            plan = Plan.objects.get(id=plan_id, user=profile)
            form = PlanForm(instance=plan)
            context = {
                'form': form,
                'plan': plan,
                'plan_id': plan_id,
            }
            return render(request, 'calendar/editcalendar.html', context)
        except Plan.DoesNotExist:
            return redirect('calendar')

    def post(self, request, plan_id):
        profile = request.user.user
        try:
            plan = Plan.objects.get(id=plan_id, user=profile)
            form = PlanForm(request.POST, instance=plan)
            if form.is_valid():
                updated_plan = form.save(commit=False)
                updated_plan.day = updated_plan.start_time.weekday()
                updated_plan.save()
                return redirect('calendar')
            context = {
                'form': form,
                'plan': plan,
                'plan_id': plan_id,
            }
            return render(request, 'calendar/editcalendar.html', context)
        except Plan.DoesNotExist:
            return redirect('calendar')
        

class DeletePlanView(LoginRequiredMixin, View):
    def post(self, request, plan_id):
        profile = request.user.user
        plan = get_object_or_404(Plan, id=plan_id, user=profile)
        plan.delete()
        return redirect('calendar')


class CalculateView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.user
        offset = int(request.GET.get('week_offset', 0))
        reference_date = datetime.today() + timedelta(weeks=offset)

        week_dates = get_week_dates(reference_date)
        start_range = week_dates[0].date()
        end_range = week_dates[-1].date()

        plans = Plan.objects.filter(
            user=profile,
            start_time__date__range=(start_range, end_range)
        ).select_related('workout')
        print(plans)
        exercise_count = plans.count()
        if exercise_count == 0:
            activity_factor = 1.2
        elif exercise_count <= 3:
            activity_factor = 1.375
        elif exercise_count <= 5:
            activity_factor = 1.55
        elif exercise_count <= 7:
            activity_factor = 1.725
        else:
            activity_factor = 1.9

        context = {
            'exercise_count': exercise_count,
            'activity_factor': activity_factor,
        }
        return render(request, 'calculate/calculate.html', context)
    
class HistoryView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.user
        offset = int(request.GET.get('week_offset', 0))
        reference_date = datetime.today() + timedelta(weeks=offset)

        week_dates = get_week_dates(reference_date)
        start_range = week_dates[0].date()
        end_range = week_dates[-1].date()

        plans = Plan.objects.filter(
            user=profile,
            start_time__date__range=(start_range, end_range)
        ).select_related('workout')
        exercise_count = plans.count()
        print(plans)
        enriched_plans = []
        for plan in plans:
            duration = get_duration_minutes(plan.start_time, plan.end_time)
            print("Duration:", duration)
            print("hour", plan.start_time.hour, "minute:", plan.start_time.minute)
            enriched_plans.append({
                'id': plan.id,
                'workout': plan.workout,
                'start_time': plan.start_time,
                'end_time': plan.end_time,
                'duration': duration,
            })
        context = {
            'plans': enriched_plans,
            'offset': offset,
            'exercise_count': exercise_count,
            'week_dates': week_dates,
            'week_range': f"{week_dates[0].strftime('%d %b')} - {week_dates[-1].strftime('%d %b %Y')}",
        }
        return render(request, 'calculate/history.html', context)