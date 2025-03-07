import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_name = f"chat_{self.user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        receiver_id = data["receiver_id"]
        message = data["message"]

        receiver = await User.objects.aget(id=receiver_id)
        msg = await Message.objects.acreate(sender=self.user, receiver=receiver, content=message)

        await self.channel_layer.group_send(
            f"chat_{receiver.id}",
            {
                "type": "chat.message",
                "message": message,
                "sender": self.user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))
