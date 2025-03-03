from django.urls import path
from .consumers import PrivateChatConsumer

websocket_urlpatterns = [
    path("ws/chat/<int:user2_id>/", PrivateChatConsumer.as_asgi()),
]
