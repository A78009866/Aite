from django.db import models
from django.conf import settings  # استخدام AUTH_USER_MODEL بشكل صحيح

class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()  # تأكد أن هذا السطر موجود
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.text[:20]}"
