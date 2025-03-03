from datetime import timedelta, datetime

import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework.test import APIClient

from travel.choices import HotelRoomTypeChoice, BookRoomStatusChoice
from travel.models import Trip, Hotel, Facility, HotelRoom, BookRoom
from user.models import User, Country, City


@pytest.mark.django_db
class TestTrip:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def db(self):
        User.objects.create(phone='+998999999999',
                            email='test@gmail.com',
                            fullname='Test',
                            is_superuser=True,
                            is_staff=True,
                            password=make_password('Jezow2000!'),
                            money=1000000)

        User.objects.create(phone='+998998888888',
                            email='test1@gmail.com',
                            fullname='Test',
                            password=make_password('Jezow2000!'),
                            money=1000000)

        Country.objects.create(name='Test')
        City.objects.create(name='Test1', country_id=1)
        City.objects.create(name='Test2', country_id=1)
        Trip.objects.create(from_city_id=1,
                            to_city_id=2,
                            price=15000,
                            details="Test",
                            duration=3,
                            overview='DFghjk',
                            start_time=datetime.now().date(),
                            end_time=datetime.now().date() + timedelta(days=3),
                            distance=200,
                            client_count=20)
        Trip.objects.create(from_city_id=2,
                            to_city_id=1,
                            price=500000,
                            details="cfgvbhnj",
                            duration=7,
                            overview='rtfgyvhbn',
                            start_time=datetime.now().date(),
                            end_time=datetime.now().date() + timedelta(days=7),
                            distance=500,
                            client_count=10)

    @pytest.fixture
    def header(self, client, db):
        url = reverse('token_obtain_pair')

        data = {
            'email': 'test@gmail.com',
            'password': 'Jezow2000!',
        }

        response = client.post(url, data)

        return {"Authorization": f"Bearer {response.data.get('access')}"}

    def test_trip_create(self, client, db, header):
        url = reverse('trip-create')

        data = {
            "price": "1000000",
            "details": "Great",
            "duration": 10,
            "overview": "Nice",
            "start_time": "2025-03-01",
            "end_time": "2025-03-04",
            "distance": 500,
            "client_count": 15,
            "from_city": 1,
            "to_city": 2
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data['duration'] = 0
        data['start_time'] = '2025-03-04'

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data = {
            "price": "1000000",
            "details": "Great",
            "duration": 5,
            "overview": "Nice",
            "start_time": "2025-03-01",
            "end_time": "2025-03-06",
            "distance": 0,
            "client_count": 15,
            "from_city": 1,
            "to_city": 2
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data['distance'] = 500
        data['client_count'] = 0

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data = {
            "price": "1000000",
            "details": "Great",
            "duration": 5,
            "overview": "Nice",
            "start_time": "2025-03-01",
            "end_time": "2025-03-06",
            "distance": 500,
            "client_count": 15,
            "from_city": 1,
            "to_city": 1
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data['to_city'] = 2
        data['price'] = '0'

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data['price'] = "1000000"

        response = client.post(url, data, headers=header)

        assert response.status_code == 201

    def test_trip_list(self, client, db):
        url = reverse('trip-list')

        response = client.get(url)

        assert response.status_code == 200

    def test_trip_detail(self, client, db):
        url = reverse('trip-detail', kwargs={"pk": 1})

        response = client.get(url)

        assert response.status_code == 200

        url = reverse('trip-detail', kwargs={"pk": 165312})

        response = client.get(url)

        assert response.status_code == 404

    def test_book_trip(self, client, db, header):
        url = reverse('trip-book')

        data = {
            "trip_id": 4512
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 500

        data = {
            "trip_id": 1
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 200

    def test_my_trip_list(self, client, db, header):
        url = reverse('trip-book')
        data = {
            "trip_id": 1
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 200

        url = reverse('my-trip-list')

        response = client.get(url, headers=header)

        assert response.status_code == 200


@pytest.mark.django_db
class TestHotel:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def db(self):
        User.objects.create(phone='+998999999999',
                            email='test@gmail.com',
                            fullname='Test',
                            is_superuser=True,
                            is_staff=True,
                            password=make_password('Jezow2000!'),
                            money=1000000)

        Country.objects.create(name='Test')
        City.objects.create(name='Test1', country_id=1)

        hotel = Hotel.objects.create(name='Test',
                                     city_id=1,
                                     lon=15.25,
                                     lat=85.65)
        Hotel.objects.create(name='fdgf',
                             city_id=1,
                             lon=15.25,
                             lat=85.65)

        facility = Facility.objects.create(name='test')

        room = HotelRoom.objects.create(hotel=hotel,
                                        room_number="15",
                                        type=HotelRoomTypeChoice.BUSINESS,
                                        count_people=2,
                                        price=15000)
        BookRoom.objects.create(room=room,
                                from_date=datetime.now() + timedelta(days=1),
                                to_date=datetime.now() + timedelta(days=8), user_id=1)
        BookRoom.objects.create(room=room,
                                from_date=datetime.now() + timedelta(days=10),
                                to_date=datetime.now() + timedelta(days=11), user_id=1,
                                status=BookRoomStatusChoice.DONE)

        hotel.facilities.add(facility)
        hotel.save()

    @pytest.fixture
    def header(self, client, db):
        url = reverse('token_obtain_pair')

        data = {
            'email': 'test@gmail.com',
            'password': 'Jezow2000!',
        }

        response = client.post(url, data)

        return {"Authorization": f"Bearer {response.data.get('access')}"}

    def test_hotel_create(self, client, header):
        url = reverse('hotel-create')

        data = {
            "name": "Test",
            "lon": "15.51",
            "lat": "82.51",
            "city": 1,
            "facilities": [
                1
            ]
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 201

    def test_hotel_list(self, client, db):
        url = reverse('hotel-list')

        response = client.get(url)

        assert response.status_code == 200

    def test_hotel_detail(self, client, db):
        url = reverse('hotel-detail', kwargs={'pk': 1})

        response = client.get(url)

        assert response.status_code == 200

        url = reverse('hotel-detail', kwargs={'pk': 1456})

        response = client.get(url)

        assert response.status_code == 404

    def test_hotel_room_detail(self, client, db):
        url = reverse('room-detail', kwargs={"pk": 1})

        response = client.get(url)

        assert response.status_code == 200

        url = reverse('room-detail', kwargs={"pk": 2651})

        response = client.get(url)

        assert response.status_code == 404

    def test_room_book(self, client, db, header):
        url = reverse('book-room')

        data = {
            "from_date": str(datetime.now().date()),
            "to_date": str(datetime.now().date() + timedelta(days=1)),
            "room": 1
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data = {
            "from_date": str(datetime.now().date() + timedelta(days=2)),
            "to_date": str(datetime.now().date() + timedelta(days=1)),
            "room": 1
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data = {
            "from_date": str(datetime.now().date() + timedelta(days=1)),
            "to_date": str(datetime.now().date() + timedelta(days=2)),
            "room": 1
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 200

    def test_room_book_list(self, client, db, header):
        url = reverse('room-book-list', kwargs={'room_id': 1})

        response = client.get(url, headers=header)

        assert response.status_code == 200

    def test_room_book_update(self, client, db, header):
        url = reverse("room-book-update", kwargs={"pk": 1})

        data = {
            'status': BookRoomStatusChoice.DONE
        }

        response = client.patch(url, data, headers=header)

        assert response.status_code == 200

    def test_hotel_review_create(self, client, db, header):
        url = reverse('hotel-review-create')

        data = {
            "review": "string",
            "rate": "1",
            "hotel": 2
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 400



        data['hotel'] = 1456

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data['hotel'] = 1

        response = client.post(url, data, headers=header)

        assert response.status_code == 201

        response = client.post(url, data, headers=header)

        assert response.status_code == 400
