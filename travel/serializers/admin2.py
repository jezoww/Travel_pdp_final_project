from rest_framework.fields import ImageField
from rest_framework.serializers import ModelSerializer

from travel.models import TripImage, HotelImage, BookRoom
from user.models import User


class HotelImageModelSerializer(ModelSerializer):
    class Meta:
        model = HotelImage
        fields = '__all__'


class TripImageModelSerializer(ModelSerializer):
    class Meta:
        model = TripImage
        fields = '__all__'


class UserAdminModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = 'fullname', 'email', 'phone'


class BookRoomListModelSerializer(ModelSerializer):
    class Meta:
        model = BookRoom
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            user = User.objects.get(id=data['user'])
            data['user'] = UserAdminModelSerializer(instance=user).data
        except:
            data['user'] = None

        return data
