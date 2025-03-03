from django.db.models import TextChoices


class TripStatusChoice(TextChoices):
    ACTIVE = 'active', 'Active'
    CANCELED = 'canceled', 'Canceled'
    OVER = 'over', 'Over'
    FULL = 'full', 'Full'


class HotelReviewRateChoice(TextChoices):
    ONE = '1', '1'
    TWO = '2', '2'
    THREE = '3', '3'
    FOUR = '4', '4'
    FIVE = '5', '5'


class HotelRoomTypeChoice(TextChoices):
    ECONOMY = 'economy', 'Economy'
    BUSINESS = 'business', 'Business'
    FIRST = 'first', 'First'


class BookRoomStatusChoice(TextChoices):
    NEW = 'new', 'New'
    PROCESS = 'process', 'Process'
    DONE = 'done', 'Done'
