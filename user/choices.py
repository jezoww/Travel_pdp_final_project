from django.db.models.enums import TextChoices


class FriendStatusChoice(TextChoices):
    WAITING = 'waiting', 'Waiting'
    FRIEND = 'friend', 'Friend'
    CANCELED = 'canceled', 'Canceled'


class TransferHistoryStatusChoice(TextChoices):
    DONE = 'done', 'Done'
    CANCELED = 'canceled', 'Canceled'
