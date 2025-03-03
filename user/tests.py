from http.client import responses

import pytest
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from user.choices import FriendStatusChoice
from user.models import User, Friend


@pytest.mark.django_db
class TestAuth:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def db(self):
        User.objects.create(id=1,
                            phone='+998998888888',
                            email='test@gmail.com',
                            username='test',
                            fullname='Test',
                            password=make_password('Jezow2000!'),
                            money=30)

        User.objects.create(id=2,
                            phone='+998999999999',
                            email='test1@gmail.com',
                            username='test1',
                            fullname='Test',
                            password=make_password('Jezow2000!'))

        User.objects.create(id=3,
                            phone='+998991111111',
                            email='test2@gmail.com',
                            username='test2',
                            fullname='Test',
                            password=make_password('Jezow2000!'))

        User.objects.create(id=4,
                            phone='+998991234567',
                            email='testgfds@gmail.com',
                            username='testhgfds',
                            fullname='Test',
                            password=make_password('Jezow2000!'))

        Friend.objects.create(user_1_id=1, user_2_id=2)
        Friend.objects.create(user_1_id=1, user_2_id=3, status=FriendStatusChoice.FRIEND)

    @pytest.fixture
    def header(self, client, db):
        url = reverse('token_obtain_pair')

        data = {
            'email': 'test@gmail.com',
            'password': 'Jezow2000!',
        }

        response = client.post(url, data)

        return {"Authorization": f"Bearer {response.data.get('access')}"}

    @pytest.fixture
    def header2(self, client, db):
        url = reverse('token_obtain_pair')

        data = {
            'email': 'test1@gmail.com',
            'password': 'Jezow2000!',
        }

        response = client.post(url, data)

        return {"Authorization": f"Bearer {response.data.get('access')}"}

    def test_register(self, client):
        url = reverse('register')

        data = {
            "fullname": "Test name",
            "email": "test@gmail.com",
            "password": "1",
            "confirm_password": "1"
        }

        response = client.post(url, data)

        assert response.status_code == 400

        data = {
            "fullname": "Test name",
            "email": "test@gmail.com",
            "password": "Jezow2000!",
            "confirm_password": "Jezow2000!e"
        }

        response = client.post(url, data)

        assert response.status_code == 400

        data['confirm_password'] = 'Jezow2000!'

        response = client.post(url, data)

        assert response.status_code == 200

        # ============================================

        url = reverse('register-phone')

        data = {
            "phone": "+998999999999",
            "email": "test1@gmail.com"
        }

        response = client.post(url, data)

        assert response.status_code == 400

        data = {
            "phone": "+998999999999",
            "email": "test@gmail.com"
        }

        response = client.post(url, data)

        assert response.status_code == 200

        # ==============================================

        url = reverse('register-phone-check')

        data = {
            "phone": "123",
            "code": "0000"
        }

        response = client.post(url, data)

        assert response.status_code == 400

        data = {
            "phone": "+998999999999",
            "code": "0000"
        }

        response = client.post(url, data)

        assert response.status_code == 400

        data['code'] = cache.get(data['phone'])

        response = client.post(url, data)

        assert response.status_code == 201

        # ===============================================

        url = reverse('register')

        data = {
            "fullname": "Test name",
            "email": "test@gmail.com",
            "password": "Jezow2000!",
            "confirm_password": "Jezow2000!"
        }

        response = client.post(url, data)

        assert response.status_code == 400

        data['email'] = 'test1@gmail.com'

        response = client.post(url, data)

        assert response.status_code == 200

        data = {
            "phone": "+998999999999",
            "email": "test1@gmail.com"
        }

        response = client.post(url, data)

        assert response.status_code == 400

    def test_login(self, client, db):
        url = reverse('token_obtain_pair')

        data = {
            "email": "test111@gmail.com",
            "password": "Jezow2000!"
        }

        response = client.post(url, data)

        assert response.status_code == 401

        data = {
            "email": "test@gmail.com",
            "password": "Jezow2000!e"
        }

        response = client.post(url, data)

        assert response.status_code == 401

        data['password'] = 'Jezow2000!'

        response = client.post(url, data)

        assert response.status_code == 200

    def test_forgot_password(self, client, db):
        url = reverse('forgot-password')

        data = {
            "email": "test11@gmail.com"
        }

        response = client.post(url, data)

        assert response.status_code == 400

        data = {
            "email": "test@gmail.com"
        }

        response = client.post(url, data)

        assert response.status_code == 200

        url = reverse('forgot-password-check')

        data = {
            "phone": "+998998888889",
            "code": "1234",
            "new_password": "Jezow2000!",
            "confirm_new_password": "Jezow2000!"
        }

        response = client.post(url, data)

        assert response.status_code == 400

        data['phone'] = '+998998888888'

        response = client.post(url, data)

        assert response.status_code == 400

        data['confirm_password'] = '1'

        response = client.post(url, data)

        assert response.status_code == 400

        data['confirm_password'] = 'Jezow2000!'

        code = cache.get('+998998888888')

        data['code'] = code

        response = client.post(url, data)

        assert response.status_code == 200

    def test_user_update(self, client, db, header):
        url = reverse('user-update')

        data = {
            'phone': '+998999999999'
        }

        response = client.patch(url, data, headers=header)

        assert response.status_code == 400

        data = {
            'fullname': 'GHjk',
            'phone': '+998995555555'
        }

        response = client.patch(url, data, headers=header)

        assert response.status_code == 200

    def test_add_friend(self, client, db, header):
        url = reverse('add-friend', kwargs={"friend_id": 1})

        response = client.get(url, headers=header)

        assert response.status_code == 400

        url = reverse('add-friend', kwargs={"friend_id": 4})

        response = client.get(url, headers=header)

        assert response.status_code == 200

        response = client.get(url, headers=header)

        assert response.status_code == 400

    def test_friend_list(self, client, db, header):
        url = reverse('friend-list')

        response = client.get(url, headers=header)

        assert response.status_code

    def test_waiting_friend_list(self, client, db, header):
        url = reverse('waiting-friend-list')

        response = client.get(url, headers=header)

        assert response.status_code

    def test_update_friend(self, client, db, header, header2):
        url = reverse('update-friend')

        data = {
            'friend': 3,
            'status': FriendStatusChoice.FRIEND
        }

        response = client.patch(url, data, headers=header2)

        assert response.status_code == 400

        data = {
            'friend': 2,
            'status': 'teststatus'
        }

        response = client.patch(url, data, headers=header)

        assert response.status_code == 400

        data = {
            'friend': 1,
            'status': FriendStatusChoice.FRIEND
        }

        response = client.patch(url, data, headers=header2)

        assert response.status_code == 200

        url = reverse('update-friend')

        data = {
            'friend': 3,
            'status': FriendStatusChoice.CANCELED
        }

        response = client.patch(url, data, headers=header)

        assert response.status_code == 200

    def test_send_money(self, client, db, header):
        url = reverse('send-money')

        data = {
            "money": "5451",
            "to_user": 2
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

        data = {
            "money": "5",
            "to_user": 5
        }
        response = client.post(url, data, headers=header)

        assert response.status_code == 404

        data = {
            "money": "10",
            "to_user": 2
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 200

    def test_transfer_history(self, client, db, header):
        url = reverse('transfer-history')

        response = client.get(url, headers=header)

        assert response.status_code == 200

    def test_add_card(self, client, db, header):
        url = reverse('add-card')

        data = {
            "number": "8600000000000001",
            "expire": "10/25",
            "cvc": 625,
            "is_default": True
        }

        response = client.post(url, data, headers=header)

        assert response.status_code == 201

        response = client.post(url, data, headers=header)

        assert response.status_code == 400

    def test_card_list(self, client, db, header):
        url = reverse('my-card-list')

        response = client.get(url, headers=header)

        assert response.status_code == 200
