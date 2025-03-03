import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.auth import AuthMiddlewareStack  # To‘g‘ri joylashuvi
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async

User = get_user_model()

class JWTAuthMiddleware:
    """
    WebSocket orqali kelgan JWT tokenni tekshiradi va foydalanuvchini scope["user"] ga qo'shadi.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])
        auth_header = headers.get(b"authorization", b"").decode()

        if auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
            try:
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await sync_to_async(User.objects.get)(id=decoded["user_id"])
                scope["user"] = user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
                scope["user"] = None
        else:
            scope["user"] = None

        return await self.inner(scope, receive, send)


# Middleware-ni AuthMiddlewareStack bilan o'rab qo'yamiz
def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
