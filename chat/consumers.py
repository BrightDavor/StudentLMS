# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage
from accounts.models import Course

class CourseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'course_{self.course_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        user = self.scope['user']

        if action == "send_message":
            message = data.get('message')
            file_url = data.get('file')  # Will implement file upload later
            chat_msg = await self.save_message(user.id, self.course_id, message, file_url)
            await self.broadcast_message(chat_msg)

        elif action == "add_reaction":
            msg_id = data.get('msg_id')
            emoji = data.get('emoji')
            updated_msg = await self.add_reaction(msg_id, emoji)
            await self.broadcast_message(updated_msg)

        elif action == "edit_message":
            msg_id = data.get('msg_id')
            new_message = data.get('new_message')
            updated_msg = await self.edit_message(msg_id, new_message)
            await self.broadcast_message(updated_msg)

        elif action == "delete_message":
            msg_id = data.get('msg_id')
            await self.delete_message(msg_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_message',
                    'msg_id': msg_id
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'msg': event['msg']
        }))

    async def delete_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'delete',
            'msg_id': event['msg_id']
        }))

    async def broadcast_message(self, chat_msg):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'msg': {
                    'id': chat_msg.id,
                    'user': chat_msg.user.first_name,
                    'message': chat_msg.message,
                    'file': chat_msg.file.url if chat_msg.file else '',
                    'reactions': chat_msg.reactions,
                    'timestamp': chat_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        )

    @database_sync_to_async
    def save_message(self, user_id, course_id, message, file_url=None):
        user = self.scope['user']
        course = Course.objects.get(id=course_id)
        msg = ChatMessage.objects.create(user=user, course=course, message=message)
        return msg

    @database_sync_to_async
    def add_reaction(self, msg_id, emoji):
        msg = ChatMessage.objects.get(id=msg_id)
        reactions = msg.reactions
        reactions[emoji] = reactions.get(emoji, 0) + 1
        msg.reactions = reactions
        msg.save()
        return msg

    @database_sync_to_async
    def edit_message(self, msg_id, new_message):
        msg = ChatMessage.objects.get(id=msg_id)
        msg.message = new_message
        msg.save()
        return msg

    @database_sync_to_async
    def delete_message(self, msg_id):
        ChatMessage.objects.filter(id=msg_id).delete()
