from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import RegisterAPIView, RegisterPhoneAPIView, RegisterCheckAPIView, ForgotPasswordAPIView, \
    ForgotPasswordCheckAPIView, UserUpdateAPIView, AddFriendAPIView, FriendListAPIView, SendMoneyAPIView, \
    WaitingFriendListAPIView, UpdateFriendAPIView, TransferHistoryListAPIView, CardCreateAPIView, MyCardListAPIView

urlpatterns = [
    path('register', RegisterAPIView.as_view(), name="register"),
    path('register/phone', RegisterPhoneAPIView.as_view(), name="register-phone"),
    path('register/phone/check', RegisterCheckAPIView.as_view(), name="register-phone-check"),
    path('login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('forgot-password-check', ForgotPasswordCheckAPIView.as_view(), name='forgot-password-check'),
    path('user-update', UserUpdateAPIView.as_view(), name='user-update'),
    path('add-friend/<int:friend_id>', AddFriendAPIView.as_view(), name='add-friend'),
    path('friend-list', FriendListAPIView.as_view(), name='friend-list'),
    path('send-money', SendMoneyAPIView.as_view(), name='send-money'),
    path('waiting-frind-list', WaitingFriendListAPIView.as_view(), name='waiting-friend-list'),
    path('update-friend', UpdateFriendAPIView.as_view(), name="update-friend"),
    path('transfer-hostory', TransferHistoryListAPIView.as_view(), name='transfer-history'),
    path('add-card', CardCreateAPIView.as_view(), name='add-card'),
    path('card-list', MyCardListAPIView.as_view(), name='my-card-list')

]
