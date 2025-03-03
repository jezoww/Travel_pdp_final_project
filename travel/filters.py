from django.db.models.aggregates import Count
from django_filters import *

from travel.models import Trip, Hotel


class TripFilter(FilterSet):
    start_time = DateFilter(field_name='start_time', lookup_expr='gte')
    end_time = DateFilter(field_name='end_time', lookup_expr='lte')
    from_city = NumberFilter(field_name='from_city_id', lookup_expr='exact')
    to_city = NumberFilter(field_name='to_city_id', lookup_expr='exact')
    from_price = NumberFilter(field_name='price', lookup_expr='gte')
    to_price = NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Trip
        fields = 'start_time', 'end_time', 'from_city', 'to_city', 'price'


class HotelFilter(FilterSet):
    # from_price = NumberFilter(field_name='rooms__price', lookup_expr='gte')
    # to_price = NumberFilter(field_name='rooms__price', lookup_expr='lte')
    city = NumberFilter(field_name='city_id', lookup_expr='exact')
    people_count = NumberFilter(method='filter_people_count')
    country_id = NumberFilter(field_name='city__country_id', lookup_expr='exact')

    class Meta:
        model = Hotel
        fields = 'city',

    def filter_people_count(self, queryset, name, value):
        return queryset.filter(rooms__count_people__gte=value)

