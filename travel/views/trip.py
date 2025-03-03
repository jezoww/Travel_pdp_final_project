from django.http import JsonResponse
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView

from travel.choices import TripStatusChoice
from travel.filters import TripFilter
from travel.models import Trip
from travel.serializers import TripModelSerializer, BookTripSerializer


@extend_schema(tags=['trip'],
               #                parameters=[
               #     OpenApiParameter(
               #         name='s_time',
               #         description="",
               #         type=OpenApiTypes.DATE,
               #         required=False,
               #     ),
               #     OpenApiParameter(
               #         name='e_time',
               #         description="",
               #         type=OpenApiTypes.DATE,
               #         required=False,
               #     ),
               #     OpenApiParameter(
               #         name='f_city',
               #         description="",
               #         type=OpenApiTypes.INT,
               #         required=False,
               #     ),
               #     OpenApiParameter(
               #         name='t_city',
               #         description="",
               #         type=OpenApiTypes.INT,
               #         required=False,
               #     ),
               #     OpenApiParameter(
               #         name='f_price',
               #         description="",
               #         type=OpenApiTypes.INT,
               #         required=False,
               #     ),
               #     OpenApiParameter(
               #         name='t_price',
               #         description="",
               #         type=OpenApiTypes.INT,
               #         required=False,
               #     )
               # ]
               )
class TripListAPIView(ListAPIView):
    queryset = Trip.objects.filter(status=TripStatusChoice.ACTIVE)
    serializer_class = TripModelSerializer
    filter_backends = DjangoFilterBackend,
    filterset_class = TripFilter


@extend_schema(tags=['trip'])
class TripRetrieveAPIView(RetrieveAPIView):
    queryset = Trip.objects.filter(status=TripStatusChoice.ACTIVE)
    serializer_class = TripModelSerializer


@extend_schema(tags=['trip'], request=BookTripSerializer)
@permission_classes([IsAuthenticated])
class BookTripAPIView(APIView):
    def post(self, request):
        data = request.data.copy()
        data['user_id'] = request.user.id
        s = BookTripSerializer(data=data)

        if s.is_valid():
            s.save()
            return JsonResponse({"message": "Trip successfully booked!"})

        return JsonResponse(s.errors, status=HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['trip'])
class MyTripListAPIView(ListAPIView):
    serializer_class = TripModelSerializer
    permission_classes = IsAuthenticated,

    def get_queryset(self):
        return self.request.user.trips.all()
