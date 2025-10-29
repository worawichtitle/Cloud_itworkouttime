from django.shortcuts import render, redirect
from django.views import View
from workout.models import *
from django.shortcuts import render, redirect
from workout.forms import *
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'logins/login.html', {"form": form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        next_path = request.GET.get("next", 'home')
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

                        return redirect('home')
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
            return redirect('home')

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
                return redirect('profile')
            
            context = {
                'user_form': user_form,
                'profile_form': profile_form
            }
            return render(request, 'homes/profile.html', context)
        except User.DoesNotExist:
            return redirect('home')
