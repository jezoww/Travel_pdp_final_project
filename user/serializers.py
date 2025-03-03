import re

from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, EmailField
from rest_framework.serializers import ModelSerializer, Serializer

from user.models import User, Country, City, Friend, TransferHistory, Card


class RegisterModelSerializer(ModelSerializer):
    confirm_password = CharField(required=True)

    class Meta:
        model = User
        fields = 'fullname', 'email', 'password', 'confirm_password', 'avatar'

        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'required': False},
            'avatar': {'required': False}
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[*/!@#$%^&(),.?\":{}|<>]", value):
            raise ValidationError("Password must contain at least one special character.")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one number.")

        confirm_password = self.initial_data.get('confirm_password')

        if value != confirm_password:
            raise ValidationError("Passwords must match!")

        return make_password(value)

    def validate_email(self, value):
        if User.objects.filter(email=value) and User.objects.filter(email=value).first().is_active:
            raise ValidationError("Email already registered!")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        validated_data['is_active'] = False
        return super().create(validated_data)


class RegisterPhoneSerializer(Serializer):
    phone = CharField(required=True)
    email = EmailField(required=True)

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if not user.exists() or user.first().is_active:
            raise ValidationError('Something went wrong!')
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise ValidationError('Phone number already registered!')
        return value


class RegisterPhoneCheckSerializer(Serializer):
    phone = CharField(required=True)
    code = CharField(required=True)

    def validate_code(self, value):
        if value != cache.get(self.initial_data.get('phone')):
            raise ValidationError('Code is incorrect!')

        return value


class ForgotPasswordSerializer(Serializer):
    email = EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("Account with this email not found!")

        return value


class ForgotPasswordCheckSerializer(Serializer):
    phone = CharField(required=True)
    code = CharField(required=True)
    new_password = CharField(required=True)
    confirm_new_password = CharField(required=True)

    def validate_code(self, value):
        if value != cache.get(self.initial_data.get('phone')):
            raise ValidationError('Code is incorrect!')

        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise ValidationError("New password must be at least 8 characters long.")
        if not re.search(r"[*/!@#$%^&(),.?\":{}|<>]", value):
            raise ValidationError("New password must contain at least one special character.")
        if not any(char.isdigit() for char in value):
            raise ValidationError("New password must contain at least one number.")

        confirm_new_password = self.initial_data.get('confirm_new_password')

        if value != confirm_new_password:
            raise ValidationError("Passwords must match!")

        return value


class CountryModelSerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CityModelSerializer(ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            country = Country.objects.get(id=data['country'])
            data['country'] = CountryModelSerializer(instance=country).data
        except:
            pass
        return data


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'fullname', 'city', 'address', 'phone', 'avatar'

        extra_kwargs = {
            'fullname': {'required': False},
            'city': {'required': False},
            'address': {'required': False},
            'phone': {'required': False},
            'avatar': {'required': False}
        }

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise ValidationError("This phone number already registered!")
        return value


class FriendModelSerializer(ModelSerializer):
    class Meta:
        model = Friend
        exclude = 'status',

        extra_kwargs = {
            'user_1': {'read_only': True}
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            user1 = User.objects.get(id=data['user_1'])
            user2 = User.objects.get(id=data['user_2'])

            user1 = UserModelSerializer(instance=user1).data
            user2 = UserModelSerializer(instance=user2).data

            user1.pop('city')
            user1.pop('address')
            user1.pop('phone')
            user2.pop('city')
            user2.pop('address')
            user2.pop('phone')

            data['user_1'] = user1
            data['user_2'] = user2
        except:
            pass

        return data


class TransferHistoryModelSerializer(ModelSerializer):
    class Meta:
        model = TransferHistory
        exclude = 'status',

        extra_kwargs = {
            "from_user": {'read_only': True}
        }

    def validate_money(self, value):
        user = User.objects.get(id=self.initial_data.get('from_user'))
        if user.money < value:
            raise ValidationError("You do not have enough money!")
        return value


class TransferHistoryListModelSerializer(ModelSerializer):
    type = CharField(required=True)

    class Meta:
        model = TransferHistory
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            to_user = User.objects.get(id=data.get('to_user'))

            to_user = UserModelSerializer(instance=to_user).data

            to_user.pop('city')
            to_user.pop('address')
            to_user.pop('phone')
        except:
            to_user = None

        data['to_user'] = to_user

        return data


class CardModelSerializer(ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

        extra_kwargs = {
            "user": {"read_only": True}
        }

    def save(self, **kwargs):
        user = kwargs.get('user')
        number = self.validated_data.get('number')
        is_default = self.validated_data.get('is_default')

        if Card.objects.filter(user=user, number=number).exists():
            raise ValidationError("This card has been already added!")

        card = Card.objects.filter(user=user, is_default=True)
        if is_default and card.exists():
            card.update(is_default=False)

        card = Card.objects.create(**self.validated_data, user=user)

        return card


