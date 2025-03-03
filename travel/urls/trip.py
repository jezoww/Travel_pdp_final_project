from django.urls import path

from travel.views import TripListAPIView, TripRetrieveAPIView, \
    BookTripAPIView, MyTripListAPIView

urlpatterns = [
    path('trip-list', TripListAPIView.as_view(), name='trip-list'),
    path('trip-detail/<int:pk>', TripRetrieveAPIView.as_view(), name='trip-detail'),
    path('trip-book', BookTripAPIView.as_view(), name='trip-book'),
    path('my-trip-list', MyTripListAPIView.as_view(), name='my-trip-list'),
]
