import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user1 = self.scope["user"]  # Middleware orqali foydalanuvchi
        if not self.user1 or self.user1.is_anonymous:
            await self.close()
            return

        self.user2_id = int(self.scope["url_route"]["kwargs"]["user2_id"])

        # Faqat tegishli userlar ulanishi mumkin
        if self.user1.id not in [self.user1.id, self.user2_id]:
            await self.close()
            return

        sorted_ids = sorted([self.user1.id, self.user2_id])
        self.room_group_name = f"private_chat_{sorted_ids[0]}_{sorted_ids[1]}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await sync_to_async(list)(Message.get_conversation(self.user1.id, self.user2_id).values("message", "from_user_id"))
        for msg in messages:
            await self.send(text_data=json.dumps(msg))

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender_id = self.user1.id

        await sync_to_async(Message.objects.create)(from_user=self.user1, to_user_id=self.user2_id, message=message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": message, "sender_id": sender_id},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"], "sender_id": event["sender_id"]}))
