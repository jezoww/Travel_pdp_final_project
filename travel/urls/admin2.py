from django.urls import path

from travel.views import TripCreateAPIView, TripImageCreateAPIView, HotelCreateAPIVIew, HotelImageCreateAPIView, \
    BookRoomListAPIView, BookRoomUpdateAPIView

urlpatterns = [
    path('trip-create', TripCreateAPIView.as_view(), name='trip-create'),
    path('trip-image-create', TripImageCreateAPIView.as_view(), name='trip-image-create'),
    path('hotel-create', HotelCreateAPIVIew.as_view(), name='hotel-create'),
    path('hotel-image-create', HotelImageCreateAPIView.as_view(), name='hotel-image-create'),
    path('room-book-list/<int:room_id>', BookRoomListAPIView.as_view(), name='room-book-list'),
    path('room-book-update/<int:pk>', BookRoomUpdateAPIView.as_view(), name='room-book-update'),
]
