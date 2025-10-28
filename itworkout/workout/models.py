from django.db import models
from django.contrib.auth.models import User as Authen

# Create your models here.
class User(models.Model):
    authen = models.OneToOneField(Authen, on_delete=models.CASCADE)
    tel = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True, default='user')  # Trainer, admin

    def __str__(self):
        return self.authen.username


class Workout(models.Model):
    name = models.CharField(max_length=255) # running, swimming, cardio
    cal125_hour = models.PositiveIntegerField()
    cal155_hour = models.PositiveIntegerField()
    cal185_hour = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.SET_NULL, null=True)
    day = models.IntegerField(choices=[(i, day) for i, day in enumerate(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.workout.name}"


class ChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_user')
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_trainer')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.id} ({self.user.username} ↔ {self.trainer.username})"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
