from datetime import datetime

from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from travel.choices import TripStatusChoice
from travel.models import Trip, TripImage
from user.models import City, User
from user.serializers import CityModelSerializer


class TripModelSerializer(ModelSerializer):
    class Meta:
        model = Trip
        exclude = 'status',

    def validate_from_city(self, value):
        to_city_id = self.initial_data.get('to_city')
        to_city = City.objects.get(id=to_city_id)

        if value == to_city:
            raise ValidationError('Starting and ending cities cannot be the same!')
        return value

    def validate_price(self, value):
        if value <= 0:
            raise ValidationError('Price cannot be 0 or under 0!')
        return value

    def validate_duration(self, value):
        start_time = datetime.strptime(self.initial_data.get('start_time', None), "%Y-%m-%d").date()
        end_time = datetime.strptime(self.initial_data.get('end_time'), "%Y-%m-%d").date()
        time = end_time - start_time
        duration = self.initial_data.get('duration')

        if time.days != int(duration):
            raise ValidationError('Start, end time and duration do not match!')

        return value

    def validate_distance(self, value):
        if value <= 0:
            raise ValidationError('Distance cannot be 0 or under 0!')
        return value

    def validate_client_count(self, value):
        if value <= 0:
            raise ValidationError('Client count cannot be 0 or under 0!')
        return value

    def validate_start_time(self, value):
        start_time = datetime.strptime(self.initial_data.get('start_time'), "%Y-%m-%d").date()
        end_time = datetime.strptime(self.initial_data.get('end_time'), "%Y-%m-%d").date()
        time = end_time - start_time

        if time.days == 0:
            raise ValidationError("Trip cannot start and end in the same day!")

        if time.days < 0:
            raise ValidationError("End time has to be bigger than start time!")

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            from_city = City.objects.get(id=data['from_city'])
            to_city = City.objects.get(id=data['to_city'])
            data['from_city'] = CityModelSerializer(instance=from_city).data
            data['to_city'] = CityModelSerializer(instance=to_city).data
            trip_images = TripImage.objects.filter(trip_id=data['id'])
            images = []
            for image in trip_images:
                images.append(image.image.url)
            data['images'] = images
            return data
        except:
            return data


class BookTripSerializer(Serializer):
    trip_id = IntegerField(required=True)
    user_id = IntegerField(required=True)
    msg = "Something went wrong!"

    def validate(self, attrs):
        user = User.objects.filter(id=attrs.get('user_id')).first()
        if not user:
            raise ValidationError(self.msg)
        trip = Trip.objects.filter(id=attrs.get('trip_id')).first()

        if not trip or trip.status != TripStatusChoice.ACTIVE:
            raise ValidationError(self.msg)

        if user.money < trip.price:
            raise ValidationError("You do not have enough money!")

        return super().validate(attrs)

    def save(self, **kwargs):
        trip = Trip.objects.get(id=self.initial_data.get('trip_id'))
        user = User.objects.get(id=self.initial_data.get('user_id'))
        user.money -= trip.price
        user.trips.add(trip)

        user.save()
        return None
