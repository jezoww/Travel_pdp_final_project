from django.urls import path

from travel.views import HotelListAPIView, HotelRetrieveAPIView, RoomRetrieveAPIView, BookRoomCreateAPIView, \
    HotelReviewCreateAPIView

urlpatterns = [
    path('hotel-list', HotelListAPIView.as_view(), name='hotel-list'),
    path('hotel-detail/<int:pk>', HotelRetrieveAPIView.as_view(), name='hotel-detail'),
    path('room-detail/<int:pk>', RoomRetrieveAPIView.as_view(), name='room-detail'),
    path('room-book', BookRoomCreateAPIView.as_view(), name='book-room'),
    path('hotel-review-craete', HotelReviewCreateAPIView.as_view(), name='hotel-review-create')
]
