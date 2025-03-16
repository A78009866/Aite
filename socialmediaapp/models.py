from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.utils import timezone

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, default="Untitled")
    image = CloudinaryField('image', default="https://res.cloudinary.com/your_cloud_name/image/upload/v1631234567/default_image.jpg", blank=True, null=True)
    video = CloudinaryField('video', blank=True, null=True)  # إضافة حقل الفيديو
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='likes')

    def __str__(self):
        return self.content[:20]


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        unique_together = ('user', 'post')  # منع الإعجاب المكرر

    def __str__(self):
        return f"{self.user.username} likes {self.post.content[:20]}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]


from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

class CustomUser(AbstractUser):
    profile_picture = CloudinaryField('image')

    @property
    def total_likes(self):
        return sum(post.likers.count() for post in self.post_set.all())

    @property
    def total_comments(self):
        return sum(post.comments.count() for post in self.post_set.all())

    @property
    def total_posts(self):
        return self.post_set.count()

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions_set",
        blank=True
    )
  
from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"من {self.sender} إلى {self.receiver}: {self.content[:30]}"

from django.db import models
from django.conf import settings

class Chat(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')  # related_name='chats'
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Chat {self.id}"