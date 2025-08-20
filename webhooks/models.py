from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class WebhookEvent(models.Model):
    EVENT_TYPES = [
        ('message', 'Message'),
        ('comment', 'Comment'),
        ('live_comment', 'Live Comment'),
        ('mention', 'Mention'),
    ]
    
    PLATFORMS = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    platform = models.CharField(max_length=10, choices=PLATFORMS)
    page_id = models.CharField(max_length=100)
    sender_id = models.CharField(max_length=100, null=True, blank=True)
    message_text = models.TextField(null=True, blank=True)
    comment_text = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField()
    raw_data = models.JSONField()
    thank_you_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.platform} {self.event_type} - {self.created_at}"

class ThankYouMessage(models.Model):
    webhook_event = models.OneToOneField(WebhookEvent, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thank you for {self.webhook_event}"