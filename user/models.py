from random import randint

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import *
from django.utils.text import slugify

from travel.models import Trip
from user.choices import FriendStatusChoice, TransferHistoryStatusChoice


class CustomUserManager(UserManager):
    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, username, password, **extra_fields)


class Country(Model):
    name = CharField(max_length=255, unique=True, null=False, blank=False)


class City(Model):
    name = CharField(max_length=255, null=False, blank=False)
    country = ForeignKey(Country, on_delete=CASCADE, related_name="cities")


class User(AbstractUser):
    phone = CharField(max_length=128, unique=True)
    first_name = None
    last_name = None
    fullname = CharField(max_length=128, null=False, blank=False)
    email = EmailField(unique=True, null=False, blank=False)
    city = ForeignKey(City, on_delete=SET_NULL, null=True, blank=True, related_name="users")
    address = CharField(max_length=555)
    passport = ImageField(upload_to='images/user_passport', null=True, blank=True)
    passport_back = ImageField(upload_to='images/user_passport', null=True, blank=True)
    money = DecimalField(max_digits=12, decimal_places=2, default=0)
    trips = ManyToManyField(Trip, related_name='users')
    is_identified = BooleanField(default=False)
    avatar = ImageField(upload_to='images/user_avatar/', null=True, blank=True)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = slugify(self.fullname)
            while User.objects.filter(username=self.username).exists():
                self.username += str(randint(0, 9))

        super().save(*args, **kwargs)


class Card(Model):
    number = CharField(max_length=17)
    expire = CharField(max_length=6)
    cvc = PositiveSmallIntegerField()
    user = ForeignKey(User, on_delete=CASCADE, related_name="cards")
    is_default = BooleanField(default=False)


class Friend(Model):
    user_1 = ForeignKey(User, on_delete=CASCADE, related_name='friends1')
    user_2 = ForeignKey(User, on_delete=CASCADE, related_name='friends2')
    status = CharField(max_length=128, choices=FriendStatusChoice, default=FriendStatusChoice.WAITING)

    class Meta:
        unique_together = 'user_1', 'user_2'


class TransferHistory(Model):
    money = DecimalField(max_digits=15, decimal_places=2)
    from_user = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='from_history')
    to_user = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='to_history')
    created_at = DateTimeField(auto_now_add=True)
    status = CharField(max_length=128, choices=TransferHistoryStatusChoice)
