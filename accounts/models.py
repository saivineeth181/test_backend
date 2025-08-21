from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FacebookUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    facebook_id = models.CharField(max_length=100, unique=True)
    access_token = models.TextField()
    token_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.facebook_id}"

class FacebookPage(models.Model):
    facebook_user = models.ForeignKey(FacebookUser, on_delete=models.CASCADE, related_name='pages')
    page_id = models.CharField(max_length=100)
    page_name = models.CharField(max_length=255)
    page_access_token = models.TextField()
    webhook_subscribed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['facebook_user', 'page_id']

    def __str__(self):
        return f"{self.page_name} ({self.page_id})"

class InstagramAccount(models.Model):
    facebook_user = models.ForeignKey(FacebookUser, on_delete=models.CASCADE, related_name='instagram_accounts')
    instagram_id = models.CharField(max_length=100)
    username = models.CharField(max_length=255)
    access_token = models.TextField()
    webhook_subscribed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['facebook_user', 'instagram_id']

    def __str__(self):
        return f"@{self.username} ({self.instagram_id})"