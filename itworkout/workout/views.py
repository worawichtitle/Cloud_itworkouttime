from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from workout.models import *
from django.shortcuts import render, redirect
from workout.forms import *
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from workout.models import ChatRoom, ChatMessage
from django.apps import apps
from django.contrib import messages
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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
        # If user is authenticated, show trainers on home page
        if request.user.is_authenticated:
            try:
                current_profile = request.user.user
            except Exception:
                current_profile = None

            profile_model = None
            if current_profile:
                profile_model = current_profile.__class__
            else:
                profile_model = apps.get_model('workout', 'User')

            if current_profile:
                trainers = profile_model.objects.filter(role='trainer').exclude(id=current_profile.id)
            else:
                trainers = profile_model.objects.filter(role='trainer')

            return render(request, 'trainers.html', {'trainers': trainers})

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
        
    
class TrainersList(LoginRequiredMixin, View):
    def get(self, request):
        # list all trainers except the current user's profile
        try:
            current_profile = request.user.user
        except Exception:
            current_profile = None

        trainers = []
        # Resolve the profile model from the workout app to avoid name collisions
        profile_model = None
        if current_profile:
            profile_model = current_profile.__class__
        else:
            profile_model = apps.get_model('workout', 'User')

        if current_profile:
            trainers = profile_model.objects.filter(role='trainer').exclude(id=current_profile.id)
        else:
            trainers = profile_model.objects.filter(role='trainer')

        return render(request, 'trainers.html', {'trainers': trainers})


class ChatList(LoginRequiredMixin, View):
    def get(self, request):
        try:
            me = request.user.user
        except Exception:
            return redirect('home')

        # rooms where the profile is either user or trainer
        rooms = ChatRoom.objects.filter(Q(user=me) | Q(trainer=me)).order_by('-created_at')
        return render(request, 'chat_list.html', {'rooms': rooms, 'me': me})


class ChatStart(LoginRequiredMixin, View):
    def get(self, request, trainer_id):
        # find trainer profile using the workout app's User (profile) model
        profile_model = apps.get_model('workout', 'User')
        trainer = get_object_or_404(profile_model, id=trainer_id)
        try:
            me = request.user.user
        except Exception:
            return redirect('trainers')

        # look for existing room either direction
        room = ChatRoom.objects.filter(user=me, trainer=trainer).first()
        if not room:
            room = ChatRoom.objects.filter(user=trainer, trainer=me).first()

        if not room:
            # create one
            room = ChatRoom.objects.create(user=me, trainer=trainer)

        return redirect(reverse('chat_room', kwargs={'room_id': room.id}))


class ChatRoomView(LoginRequiredMixin, View):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        try:
            me = request.user.user
        except Exception:
            return redirect('trainers')

        # security: ensure user is participant
        if me != room.user and me != room.trainer:
            return HttpResponseForbidden('Not a participant of this chat')

        messages = room.messages.order_by('sent_at')[:500]
        other_user = room.trainer if me == room.user else room.user
        return render(request, 'chat_room.html', {'room': room, 'messages': messages, 'me': me, 'other_user': other_user})

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        me = request.user.user

        if me != room.user and me != room.trainer:
            return HttpResponseForbidden('Not a participant of this chat')

        message = request.POST.get('message')
        if message:
            ChatMessage.objects.create(
                room=room,
                sender=me,
                content=message
            )
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect('chat_room', room_id=room_id)


class ChatMessagesView(LoginRequiredMixin, View):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        me = request.user.user

        if me != room.user and me != room.trainer:
            return HttpResponseForbidden('Not a participant of this chat')

        messages = room.messages.order_by('sent_at')[:500]
        other_user = room.trainer if me == room.user else room.user
        return render(request, 'messages_content.html', {
            'messages': messages,
            'request': request,
            'other_user': other_user
        })


class ChatUpdatesView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            me = request.user.user
        except Exception:
            return JsonResponse({'error': 'not authenticated'}, status=403)

        rooms = ChatRoom.objects.filter(Q(user=me) | Q(trainer=me)).order_by('-created_at')
        data = []
        for room in rooms:
            last = room.messages.order_by('-sent_at').first()
            if not last:
                continue
            other = room.trainer if me == room.user else room.user
            data.append({
                'room_id': room.id,
                'other_username': other.authen.username,
                'last_message': last.content[:120],
                'last_sent_at': last.sent_at.isoformat()
            })

        return JsonResponse({'rooms': data})





@login_required
@require_POST
def chat_delete(request, room_id):
    """Delete the chat room and its messages. Only a participant can delete a room."""
    room = get_object_or_404(ChatRoom, id=room_id)
    try:
        me = request.user.user
    except Exception:
        return JsonResponse({'error': 'no profile'}, status=403)

    if me != room.user and me != room.trainer:
        return JsonResponse({'error': 'not participant'}, status=403)

    # capture participant ids before deleting
    user_id = room.user.id
    trainer_id = room.trainer.id

    # delete room (messages cascade)
    room.delete()

    # notify both participants (if connected) that the room was deleted
    channel_layer = get_channel_layer()
    payload = {
        'event': 'chat_deleted',
        'room_id': room_id,
    }

    async_to_sync(channel_layer.group_send)(f'user_{user_id}', {
        'type': 'user.notification',
        'payload': payload,
    })
    async_to_sync(channel_layer.group_send)(f'user_{trainer_id}', {
        'type': 'user.notification',
        'payload': payload,
    })

    return JsonResponse({'status': 'ok', 'redirect': reverse('chat_list')})
