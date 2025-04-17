import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Getting the room name dynamically from the URL, such as 'user1' or 'user2'
        self.room_name = self.scope['url_route']['kwargs']['recipient']
        self.room_group_name = f'chat_{self.room_name}'

        # Join the chat room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive the message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']

        # Send the message to the chat room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # This refers to the method to be called when broadcasting
                'message': message,
                'sender': sender
            }
        )

    async def chat_message(self, event):
        # Broadcast message to WebSocket clients
        message = event['message']
        sender = event['sender']

        # Send the message to WebSocket client (this client receives the message)
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
