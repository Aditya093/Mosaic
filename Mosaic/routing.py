# Import necessary modules and functions
from django.urls import path, re_path
from Mosaic import consumers

# Define WebSocket URL patterns
websocket_urlpatterns = [
    # WebSocket URL pattern for handling chat room connections
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]
