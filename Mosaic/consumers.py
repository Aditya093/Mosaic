import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from django.utils import timezone

from Mosaic.models import Message
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name=self.scope['url_route']['kwargs']['room_name'][0]
        self.room_group_name='chat_%s' % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
           
    
    async def receive(self,text_data):
        print(text_data)
        text_data_json=json.loads(text_data)
        message=text_data_json["content"] 
        sender=text_data_json['sender']
        receiver=text_data_json['receiver']
        sender_name=text_data_json['sender']
        await self.save_message(sender,message,receiver)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'receiver':receiver,
                'sender':sender,
                'sender_name':sender_name,
                'timestamp':timezone.now().strftime('%b. %d, %Y, %I:%M %p')
                
            },
        )
    async def chat_message(self,event):
        message=event['message']
        sender=event['sender']
        receiver=event['receiver']
        sender_name=event['sender_name']
        await self.send(
            text_data=json.dumps(
                {
                    'message':message,
                    'sender_name':sender_name,
                    'receiver':receiver,
                    'sender':sender,
                    'timestamp':timezone.now().strftime('%b. %d, %Y, %I:%M %p')
                }
            )
        )   
    @database_sync_to_async
    def save_message(self,sender,message,receiver):
        sender_user=User.objects.get(id=sender)
        receiver_user=User.objects.get(id=receiver)
        new_message=Message.objects.create(sender=sender_user,content=message,receiver=receiver_user)
        new_message.save()