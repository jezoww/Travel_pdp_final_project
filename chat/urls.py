from django.urls import path
from .views import chat_view, LoginView

urlpatterns = [
    path('login', LoginView.as_view()),
    path('chat/<int:user2_id>/', chat_view, name='chat_view'),
]
