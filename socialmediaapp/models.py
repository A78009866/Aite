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
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='likes')
    audio = models.FileField(upload_to="audio/", blank=True, null=True)  # ✅ حقل الصوت
    video = CloudinaryField('video', resource_type="video", blank=True, null=True)  # ✅ الفيديو

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


from django.core.exceptions import ValidationError
import re

def validate_no_html(value):
    if re.search(r'<[^>]+>', value):
        raise ValidationError('ممنوع استخدام علامات HTML!')



class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(validators=[validate_no_html])  # أضف التحقق هنا
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]


from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

from django.db import models

class CustomUser(AbstractUser):
    profile_picture = CloudinaryField('image')
    last_activity = models.DateTimeField(auto_now=True)  # أضف هذا الحقل
    
    @property
    def is_online(self):
        """تحقق إذا كان المستخدم متصل الآن (في آخر 5 دقائق)"""
        from django.utils import timezone
        now = timezone.now()
        return (now - self.last_activity).total_seconds() < 300  # 5 دقائق
    
    @property
    def is_verified(self):
        return self.followers.count() > 10

    @property
    def followers_count(self):
        return self.followers.count()

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
    
    def clean(self):
        validate_no_html(self.username)
        super().clean()
        
from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)  # إضافة هذا الحقل الجديد
    
    def __str__(self):
        return f"من {self.sender} إلى {self.receiver}: {self.content[:30]}"
    
    def mark_as_seen(self):
        if not self.is_read:
            self.is_read = True
            self.seen_at = timezone.now()
            self.save()

from django.db import models
from django.conf import settings

class Chat(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')  # related_name='chats'
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Chat {self.id}"

from django.db import models
from django.conf import settings

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')  # منع متابعة نفس الشخص أكثر من مرة

    def __str__(self):
        return f"{self.follower.username} يتابع {self.followed.username}"

from django.db import models
from django.conf import settings

class Story(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = CloudinaryField('image', default="https://res.cloudinary.com/your_cloud_name/image/upload/v1631234567/default_image.jpg", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Story by {self.user.username}"

        # أضف هذا في نهاية ملف models.py
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'إعجاب'),
        ('comment', 'تعليق'),
        ('follow', 'متابعة'),
        ('mention', 'ذكر'),
        ('message', 'رسالة'),
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(null=True, blank=True)  # حقل جديد لتخزين محتوى الإشعار
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} - {self.get_notification_type_display()} - {self.recipient.username}"
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} - {self.get_notification_type_display()} - {self.recipient.username}"


class Family(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_families')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='families')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class FamilyPost(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    audio = models.FileField(upload_to="audio/", blank=True, null=True)
    video = CloudinaryField('video', resource_type="video", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='family_likes')

    def __str__(self):
        return f"{self.user.username} in {self.family.name}"

class Reel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = CloudinaryField('video', resource_type="video")
    caption = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='reel_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reel by {self.user.username}"
    
    @property
    def like_count(self):
        return self.likes.count()
