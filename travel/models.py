from django.db.models import *

from travel.choices import TripStatusChoice, HotelRoomTypeChoice, HotelReviewRateChoice, BookRoomStatusChoice


class Trip(Model):
    from_city = ForeignKey('user.City', on_delete=CASCADE, related_name='from_trips')
    to_city = ForeignKey('user.City', on_delete=CASCADE, related_name='to_trips')
    price = DecimalField(max_digits=10, decimal_places=2)
    details = TextField()
    duration = PositiveSmallIntegerField()
    overview = TextField()
    start_time = DateField()
    end_time = DateField()
    distance = PositiveSmallIntegerField()
    status = CharField(max_length=128, choices=TripStatusChoice, default=TripStatusChoice.ACTIVE)
    client_count = PositiveSmallIntegerField()


class TripImage(Model):
    image = ImageField('images/trip/')
    trip = ForeignKey(Trip, on_delete=CASCADE, related_name='images')


# ===============================================

class Facility(Model):
    name = CharField(max_length=128)
    image = ImageField(upload_to='images/facilities/', null=False, blank=False)


class Hotel(Model):
    name = CharField(max_length=127)
    city = ForeignKey('user.City', on_delete=CASCADE, related_name='hotels')
    lon = DecimalField(max_digits=11, decimal_places=8)
    lat = DecimalField(max_digits=11, decimal_places=8)
    facilities = ManyToManyField(Facility, related_name='hotels')


class HotelImage(Model):
    image = ImageField(upload_to='images/hotels/')
    hotel = ForeignKey(Hotel, on_delete=CASCADE, related_name='images')


class HotelRoom(Model):
    hotel = ForeignKey(Hotel, on_delete=CASCADE, related_name='rooms')
    room_number = CharField(max_length=15)
    price = DecimalField(max_digits=12, decimal_places=2)
    type = CharField(max_length=128, choices=HotelRoomTypeChoice)
    count_people = PositiveSmallIntegerField()


class RoomImage(Model):
    image = ImageField(upload_to='images/rooms/')
    room = ForeignKey(HotelRoom, on_delete=CASCADE, related_name='images')


class HotelReview(Model):
    user = ForeignKey('user.User', on_delete=CASCADE, related_name='reviews')
    hotel = ForeignKey(Hotel, on_delete=CASCADE, related_name='reviews')
    review = CharField(max_length=128)
    rate = CharField(max_length=2, choices=HotelReviewRateChoice)


class BookRoom(Model):
    room = ForeignKey(HotelRoom, on_delete=CASCADE, related_name='books')
    from_date = DateField()
    to_date = DateField()
    user = ForeignKey('user.User', on_delete=CASCADE, related_name='books')
    status = CharField(max_length=128, choices=BookRoomStatusChoice, default=BookRoomStatusChoice.NEW)
