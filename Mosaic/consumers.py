# Import necessary modules and functions
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from django.utils import timezone
from Mosaic.models import Message

# Define a WebSocket consumer class for handling chat functionality
class ChatConsumer(AsyncWebsocketConsumer):
    # Method called when a new WebSocket connection is established
    async def connect(self):
        # Extract the room name from the URL route parameters
        self.room_name = self.scope['url_route']['kwargs']['room_name'][0]
        # Construct the group name for this chat room
        self.room_group_name = 'chat_%s' % self.room_name
        # Add the channel to the group for this chat room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accept the WebSocket connection
        await self.accept()
        
    # Method called when the WebSocket connection is closed
    async def disconnect(self, close_code):
        # Remove the channel from the group for this chat room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Method called when a message is received from the WebSocket
    async def receive(self, text_data):
        # Deserialize the received JSON data
        text_data_json = json.loads(text_data)
        # Extract message content, sender, and receiver from the received data
        message = text_data_json["content"]
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']
        sender_name = text_data_json['sender']
        # Save the message to the database asynchronously
        await self.save_message(sender, message, receiver)
        # Broadcast the received message to all users in the chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'receiver': receiver,
                'sender': sender,
                'sender_name': sender_name,
                'timestamp': timezone.now().strftime('%b. %d, %Y, %I:%M %p')
            },
        )
    
    # Method called when a chat message is received from the group
    async def chat_message(self, event):
        # Extract message details from the event
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        sender_name = event['sender_name']
        # Send the message back to the WebSocket client
        await self.send(
            text_data=json.dumps(
                {
                    'message': message,
                    'sender_name': sender_name,
                    'receiver': receiver,
                    'sender': sender,
                    'timestamp': timezone.now().strftime('%b. %d, %Y, %I:%M %p')
                }
            )
        )   
    
    # Method to save the message to the database asynchronously
    @database_sync_to_async
    def save_message(self, sender, message, receiver):
        # Retrieve sender and receiver user objects from the database
        sender_user = User.objects.get(id=sender)
        receiver_user = User.objects.get(id=receiver)
        # Create a new message object and save it to the database
        new_message = Message.objects.create(sender=sender_user, content=message, receiver=receiver_user)
        new_message.save()
