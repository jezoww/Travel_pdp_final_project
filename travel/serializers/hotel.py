from datetime import datetime, timedelta

from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from travel.choices import BookRoomStatusChoice
from travel.models import Hotel, Facility, HotelRoom, RoomImage, HotelReview, BookRoom
from user.models import City, User
from user.serializers import CityModelSerializer


class FacilityModelSerializer(ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'


class HotelModelSerializer(ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        hotel = Hotel.objects.get(id=data['id'])

        data['facilities'] = FacilityModelSerializer(instance=hotel.facilities.all(), many=True).data

        hotel_images = hotel.images.all()
        images = []
        for image in hotel_images:
            images.append(image.image.url)

        data['images'] = images

        try:
            city = City.objects.get(id=data['city'])
            data['city'] = CityModelSerializer(instance=city).data
        except:
            pass

        reviews = hotel.reviews.all()

        sum_review = 0

        for review in reviews:
            sum_review += int(review.rate)

        try:
            data['rate'] = sum_review / reviews.count()
        except:
            data['rate'] = 0

        return data


class HotelRoomModelSerializer(ModelSerializer):
    class Meta:
        model = HotelRoom
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        room_images = RoomImage.objects.filter(room_id=data['id'])

        images = []

        for image in room_images:
            images.append(image.image.url)

        data['images'] = images

        return data


class HotelReviewUserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = 'fullname', 'avatar'


class HotelReviewModelSerializer(ModelSerializer):
    class Meta:
        model = HotelReview
        fields = '__all__'

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def validate(self, attrs):
        hotel_id = attrs.get('hotel')
        user = self.context.get('request').user

        if not user or not hotel_id:
            raise ValidationError("Something went wrong!")
        if not BookRoom.objects.filter(user=user, room__hotel_id=hotel_id, status=BookRoomStatusChoice.DONE).exists():
            raise ValidationError("You cannot!")
        if HotelReview.objects.filter(hotel_id=hotel_id, user=user).exists():
            raise ValidationError("You cannot send review more than 1!")

        return super().validate(attrs)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            print(data.get('user'))
            print(data.get('user_id'))
            review_user = User.objects.get(id=data.get('user'))
            print(review_user)
            user = HotelReviewUserModelSerializer(instance=review_user).data
            print(user)
            data['user'] = user
        except:
            data['user'] = None

        return data


class HotelDetailModelSerializer(ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        hotel = Hotel.objects.get(id=data['id'])

        data['facilities'] = FacilityModelSerializer(instance=hotel.facilities.all(), many=True).data

        hotel_images = hotel.images.all()
        images = []
        for image in hotel_images:
            images.append(image.image.url)

        data['images'] = images

        try:
            city = City.objects.get(id=data['city'])
            data['city'] = CityModelSerializer(instance=city).data
        except:
            pass

        reviews = hotel.reviews.all()

        sum_review = 0

        for review in reviews:
            sum_review += int(review.rate)

        try:
            data['rate'] = sum_review / reviews.count()
        except:
            data['rate'] = 0

        hotel_rooms = HotelRoom.objects.filter(hotel_id=data['id'])
        rooms = HotelRoomModelSerializer(instance=hotel_rooms, many=True).data

        data['rooms'] = rooms

        hotel_reviews = HotelReview.objects.filter(hotel_id=data['id'])

        reviews = HotelReviewModelSerializer(instance=hotel_reviews, many=True).data
        data['reviews'] = reviews

        return data


class BookRoomModelSerializer(ModelSerializer):
    class Meta:
        model = BookRoom
        fields = 'user', 'from_date', 'to_date', 'room'

        # extra_kwargs = {
        #     'user': {'read_only': True}
        # }

    msg = "Something went wrong!"

    def validate_from_date(self, value):
        to_date = self.initial_data.get('to_date')
        end = datetime.strptime(to_date, '%Y-%m-%d').date()

        if value >= end or value <= datetime.now().date():
            raise ValidationError("You chose invalid time!")
        return value

    def validate(self, attrs):
        user = attrs.get('user')
        if not user:
            raise ValidationError(self.msg)
        room = attrs.get('room')

        if not room:
            raise ValidationError(self.msg)

        if user.money < room.price:
            raise ValidationError("You do not have enough money!")

        return super().validate(attrs)


class RoomDetailModelSerializer(ModelSerializer):
    class Meta:
        model = HotelRoom
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        room_booked_dates = BookRoom.objects.filter(~Q(status=BookRoomStatusChoice.DONE) & Q(room_id=data['id']))

        booked_dates = BookRoomModelSerializer(instance=room_booked_dates, many=True).data

        dates = set()

        for date in booked_dates:
            start_date = date['from_date']
            end_date = date['to_date']

            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            # from_date dan to_date gacha bo‘lgan kunlarni qo‘shish
            current_date = start
            while current_date <= end:
                dates.add(current_date)
                current_date += timedelta(days=1)

        dates_list = sorted(list(dates))

        data['dates_list'] = dates_list

        room_images = RoomImage.objects.filter(room_id=data['id'])

        images = []

        for image in room_images:
            images.append(image.image.url)

        data['images'] = images

        # BookRoom.objects.create(room_id=data['id'], from_date=datetime.now() + timedelta(days=1), to_date=datetime.now() + timedelta(days=8), user_id=3)
        # BookRoom.objects.create(room_id=data['id'], from_date=datetime.now() + timedelta(days=10), to_date=datetime.now() + timedelta(days=11), user_id=3)

        return data
