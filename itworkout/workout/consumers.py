import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from .models import ChatRoom, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data.get('message')

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            return

        # persist message
        await self.save_message(self.room_id, user, message)

        payload = {
            'message': message,
            'sender_username': user.username,
            'sender_id': user.id,
            'sent_at': timezone.now().isoformat(),
        }

        # broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'payload': payload,
            }
        )

    async def chat_message(self, event):
        payload = event['payload']
        await self.send(text_data=json.dumps(payload))

    @database_sync_to_async
    def save_message(self, room_id, user, message):
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

        # user is Django auth user; ChatMessage expects workout.User
        # map django user -> profile
        try:
            profile = user.user
        except Exception:
            profile = None

        if profile:
            ChatMessage.objects.create(room=room, sender=profile, content=message)
        return None


class NotificationConsumer(AsyncWebsocketConsumer):
    """A simple per-user notification channel.

    Clients should connect to /ws/notifications/ and the consumer will add them
    to a group named `user_{profile_id}` so server-side code can push events to
    individual users (for example, chat deletions).
    """
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return

        try:
            profile = user.user
        except Exception:
            await self.close()
            return

        self.user_group_name = f'user_{profile.id}'
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def user_notification(self, event):
        # forward payload to WebSocket client
        payload = event.get('payload', {})
        await self.send(text_data=json.dumps(payload))
