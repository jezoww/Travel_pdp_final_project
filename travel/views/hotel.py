from django.db.models.aggregates import Count
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from travel.filters import HotelFilter
from travel.models import Hotel, HotelRoom, BookRoom, HotelReview, Trip
from travel.serializers import HotelModelSerializer, \
    HotelDetailModelSerializer, RoomDetailModelSerializer, BookRoomModelSerializer, HotelReviewModelSerializer


@extend_schema(tags=['hotel'])
class HotelListAPIView(ListAPIView):
    serializer_class = HotelModelSerializer
    filter_backends = DjangoFilterBackend,
    filterset_class = HotelFilter

    def get_queryset(self):
        return Hotel.objects.annotate(count_reviews=Count('reviews')).order_by('-count_reviews').all()


@extend_schema(tags=['hotel'])
class HotelRetrieveAPIView(RetrieveAPIView):
    serializer_class = HotelDetailModelSerializer
    queryset = Hotel.objects.all()
    lookup_field = 'pk'


@extend_schema(tags=['hotel'])
class RoomRetrieveAPIView(RetrieveAPIView):
    serializer_class = RoomDetailModelSerializer
    queryset = HotelRoom.objects.all()
    lookup_field = 'pk'


# @extend_schema(tags=['hotel'], request=BookRoomModelSerializer)
# class BookRoomCreateAPIView(CreateAPIView):
#     queryset = BookRoom
#     serializer_class = BookRoomModelSerializer
#     permission_classes = IsAuthenticated,
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


@extend_schema(tags=['hotel'], request=BookRoomModelSerializer)
@permission_classes([IsAuthenticated])
class BookRoomCreateAPIView(APIView):
    def post(self, request):
        data = request.data.copy()
        user = self.request.user
        data['user'] = user.id

        s = BookRoomModelSerializer(data=data)

        if s.is_valid():
            data = {
                "message": "Success!"
            }
            price = HotelRoom.objects.get(id=request.data.get('room')).price

            user.money -= price
            user.save()

            s.save()

            return JsonResponse(data)

        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['hotel'], request=HotelReviewModelSerializer)
class HotelReviewCreateAPIView(CreateAPIView):
    serializer_class = HotelReviewModelSerializer
    queryset = HotelReview.objects.all()
    permission_classes = IsAuthenticated,

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
