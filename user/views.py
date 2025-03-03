from decimal import Decimal
from random import randint

from django.core.cache import cache
from django.db.models import Case, When, Value, CharField
from django.db.models import Q
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import permission_classes
from rest_framework.generics import UpdateAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, \
    HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from user.choices import FriendStatusChoice, TransferHistoryStatusChoice
from user.models import User, Friend, TransferHistory, Card
from user.serializers import RegisterModelSerializer, RegisterPhoneSerializer, RegisterPhoneCheckSerializer, \
    ForgotPasswordSerializer, ForgotPasswordCheckSerializer, UserModelSerializer, FriendModelSerializer, \
    TransferHistoryModelSerializer, TransferHistoryListModelSerializer, CardModelSerializer
from user.tasks import send_sms


@extend_schema(tags=['auth'], request=RegisterModelSerializer)
class RegisterAPIView(APIView):
    def post(self, request):
        s = RegisterModelSerializer(data=request.data)

        if s.is_valid():
            s.save()
            data = {"message": "Please enter your phone number!", "msg_admin": "User created with false active!"}

            return JsonResponse(data)

        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=RegisterPhoneSerializer)
class RegisterPhoneAPIView(APIView):
    def post(self, request):
        s = RegisterPhoneSerializer(data=request.data)

        if s.is_valid():
            email = s.validated_data.get('email')
            phone = s.validated_data.get('phone')
            user = User.objects.get(email=email)
            user.phone = phone
            user.save()
            code = randint(1000, 9999)
            print(code)
            sent = send_sms.delay(phone, code)
            if sent:
                cache.set(phone, str(code), timeout=300)
                data = {"message": f"Code sent to {phone}"}
                return JsonResponse(data)
            data = {'message': f"Cannot send code to {phone}"}
            return JsonResponse(data, status=HTTP_500_INTERNAL_SERVER_ERROR)
        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=RegisterPhoneCheckSerializer)
class RegisterCheckAPIView(APIView):
    def post(self, request):

        phone = request.data.get('phone')

        if not User.objects.filter(phone=phone):
            data = {'message': 'Something went wrong!'}
            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        if not cache.get(phone, None):
            data = {'message': "Code expired!"}
            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        s = RegisterPhoneCheckSerializer(data=request.data)

        if s.is_valid():
            phone = s.validated_data.get('phone')
            user = User.objects.get(phone=phone)
            user.is_active = True
            user.save()
            data = {'message': 'Successfully registered!'}
            return JsonResponse(data, status=HTTP_201_CREATED)
        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=ForgotPasswordSerializer)
class ForgotPasswordAPIView(APIView):
    def post(self, request):
        s = ForgotPasswordSerializer(data=request.data)

        if s.is_valid():
            phone = User.objects.get(email=s.validated_data.get('email')).phone
            code = randint(1000, 9999)
            print(code)
            sent = send_sms.delay(phone, code)
            if sent:
                cache.set(phone, str(code), timeout=300)
                data = {"message": f"Code sent to {phone}"}
                return JsonResponse(data)
            data = {'message': f"Cannot send code to {phone}"}
            return JsonResponse(data, status=HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=ForgotPasswordCheckSerializer)
class ForgotPasswordCheckAPIView(APIView):
    def post(self, request):
        phone = request.data.get('phone')

        if not User.objects.filter(phone=phone):
            data = {'message': 'Something went wrong!'}

            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        if not cache.get(phone, None):
            data = {'message': "Code expired!"}

            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        s = ForgotPasswordCheckSerializer(data=request.data)

        if s.is_valid():
            phone = s.validated_data.get('phone')
            user = User.objects.get(phone=phone)
            new_password = s.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()
            data = {'message': 'Password successfully updated!'}

            return JsonResponse(data, status=HTTP_200_OK)

        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=UserModelSerializer)
class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserModelSerializer
    queryset = User.objects.all()
    permission_classes = IsAuthenticated,

    def get_object(self):
        return self.request.user


@extend_schema(tags=['auth'], request=FriendModelSerializer)
@permission_classes([IsAuthenticated])
class AddFriendAPIView(APIView):
    def get(self, request, friend_id):
        user_id = self.request.user.id
        if user_id == friend_id:
            data = {
                "message": "You cannot be friend to yourself!"
            }

            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        if Friend.objects.filter(user_1_id=user_id, user_2_id=friend_id).exists() or Friend.objects.filter(
                user_2_id=user_id, user_1_id=friend_id).exists():
            data = {
                "message": "They are already friends!"
            }

            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        Friend.objects.create(user_1_id=user_id, user_2_id=friend_id)

        data = {
            "message": "Your request sent!"
        }

        return JsonResponse(data)


@extend_schema(tags=['auth'])
@permission_classes([IsAuthenticated])
class FriendListAPIView(ListAPIView):
    serializer_class = FriendModelSerializer

    def get_queryset(self):
        return Friend.objects.filter(
            (Q(user_1=self.request.user) | Q(user_2=self.request.user)) & Q(status=FriendStatusChoice.FRIEND))


@extend_schema(tags=['auth'])
@permission_classes([IsAuthenticated])
class WaitingFriendListAPIView(ListAPIView):
    serializer_class = FriendModelSerializer

    def get_queryset(self):
        return Friend.objects.filter(user_2=self.request.user, status=FriendStatusChoice.WAITING)


@extend_schema(tags=['auth'], parameters=[
    OpenApiParameter(
        name='friend',
        type=int,
        required=True,
        description='...',
    ),
    OpenApiParameter(
        name='status',
        type=str,
        required=True,
        enum=['canceled', 'friend']
    )
])
@permission_classes([IsAuthenticated])
class UpdateFriendAPIView(APIView):
    def patch(self, request):
        data = request.data
        friend = data.get('friend')
        # friend = request.query_params.get('friend')
        if not friend:
            data = {
                "message": "Friend is requires!"
            }

            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        user_1 = int(friend)
        user_2 = request.user.id

        status = data.get('status')
        # status = request.query_params.get('status')
        if not status in FriendStatusChoice:
            data = {
                "message": "Incorrect status!"
            }

            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        if data.get('status') == FriendStatusChoice.WAITING or (
                not Friend.objects.filter(user_1_id=user_1, user_2_id=user_2).exists() and not Friend.objects.filter(
            user_1_id=user_2, user_2_id=user_1).exists()):
            data = {
                "message": "Something went wrong!"
            }

            return JsonResponse(data, status=HTTP_400_BAD_REQUEST)

        friend = Friend.objects.filter(user_1_id=user_1, user_2_id=user_2)

        if not friend.exists():
            friend = Friend.objects.filter(user_1_id=user_2, user_2_id=user_1)

        friend.update(status=status)

        data = {
            "message": "Success"
        }

        return JsonResponse(data)


@extend_schema(tags=['auth'], request=TransferHistoryModelSerializer)
@permission_classes([IsAuthenticated])
class SendMoneyAPIView(APIView):
    def post(self, request):
        data = request.data.copy()
        data['from_user'] = request.user.id

        s = TransferHistoryModelSerializer(data=data)
        from_user = request.user
        try:
            to_user = User.objects.get(id=data.get('to_user'))
        except:
            return JsonResponse({"message": "User not found!"}, status=HTTP_404_NOT_FOUND)
        money = data.get('money')

        if s.is_valid():
            from_user.money -= Decimal(money)
            to_user.money += Decimal(money)

            from_user.save()
            to_user.save()

            TransferHistory.objects.create(from_user=from_user,
                                           to_user=to_user,
                                           money=money,
                                           status=TransferHistoryStatusChoice.DONE)

            data = {
                "message": "Success!"
            }

            return JsonResponse(data)
        TransferHistory.objects.create(from_user=from_user,
                                       to_user=to_user,
                                       money=money,
                                       status=TransferHistoryStatusChoice.CANCELED)

        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=TransferHistoryListModelSerializer)
@permission_classes([IsAuthenticated])
class TransferHistoryListAPIView(ListAPIView):
    serializer_class = TransferHistoryListModelSerializer

    def get_queryset(self):
        return TransferHistory.objects.filter(Q(from_user=self.request.user) | Q(to_user=self.request.user)).annotate(
            type=Case(
                When(from_user=self.request.user, then=Value('sender')),
                When(to_user=self.request.user, then=Value('receiver')),
                default=Value('unknown'),
                output_field=CharField()
            )
        ).order_by('-created_at')


@extend_schema(tags=['auth'], request=CardModelSerializer)
@permission_classes([IsAuthenticated])
class CardCreateAPIView(CreateAPIView):
    queryset = Card.objects.all()
    serializer_class = CardModelSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['auth'], request=CardModelSerializer)
@permission_classes([IsAuthenticated])
class MyCardListAPIView(ListAPIView):
    serializer_class = CardModelSerializer

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)
