from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from travel.choices import BookRoomStatusChoice
from travel.models import Trip, Hotel, TripImage, HotelImage, BookRoom
from travel.serializers import TripModelSerializer, HotelModelSerializer, TripImageModelSerializer, \
    HotelImageModelSerializer, BookRoomListModelSerializer


@extend_schema(tags=['admin'], request=TripModelSerializer)
class TripCreateAPIView(CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripModelSerializer
    permission_classes = IsAuthenticated, IsAdminUser


@extend_schema(tags=['admin'], request=HotelModelSerializer)
class HotelCreateAPIVIew(CreateAPIView):
    serializer_class = HotelModelSerializer
    queryset = Hotel.objects.all()
    permission_classes = IsAuthenticated, IsAdminUser


@extend_schema(tags=['admin'], request=TripImageModelSerializer)
class TripImageCreateAPIView(CreateAPIView):
    queryset = TripImage.objects.all()
    serializer_class = TripImageModelSerializer
    permission_classes = IsAuthenticated, IsAdminUser


@extend_schema(tags=['admin'], request=HotelImageModelSerializer)
class HotelImageCreateAPIView(CreateAPIView):
    serializer_class = HotelImageModelSerializer
    queryset = HotelImage.objects.all()
    permission_classes = IsAuthenticated, IsAdminUser


@extend_schema(tags=['admin'])
class BookRoomListAPIView(ListAPIView):
    serializer_class = BookRoomListModelSerializer
    permission_classes = IsAdminUser,

    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return BookRoom.objects.filter(Q(room_id=room_id) & ~Q(status=BookRoomStatusChoice.DONE))


@extend_schema(tags=['admin'])
class BookRoomUpdateAPIView(UpdateAPIView):
    queryset = BookRoom.objects.all()
    serializer_class = BookRoomListModelSerializer
    permission_classes = IsAdminUser,
