import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns
from chat.middleware import JWTAuthMiddlewareStack  # To'g'ri middleware ni chaqiramiz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
