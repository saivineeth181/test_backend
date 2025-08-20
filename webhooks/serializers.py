# webhooks/serializers.py
from rest_framework import serializers
from .models import WebhookEvent, ThankYouMessage

class ThankYouMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThankYouMessage
        fields = ['message', 'sent_at']

class WebhookEventSerializer(serializers.ModelSerializer):
    thank_you_message = ThankYouMessageSerializer(read_only=True)
    
    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'event_type', 'platform', 'page_id', 'sender_id',
            'message_text', 'comment_text', 'timestamp', 'thank_you_sent',
            'created_at', 'thank_you_message'
        ]