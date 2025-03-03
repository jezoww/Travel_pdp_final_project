from django.db import models
from user.models import User
from django.db.models import Q

class Message(models.Model):
    message = models.CharField(max_length=128)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_messages')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_messages')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}: {self.message}"

    @staticmethod
    def get_conversation(user1, user2):
        return Message.objects.filter(
            Q(from_user=user1, to_user=user2) | Q(from_user=user2, to_user=user1)
        ).select_related('from_user', 'to_user').order_by('created_at')
