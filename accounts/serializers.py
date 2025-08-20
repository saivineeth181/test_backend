from rest_framework import serializers
from .models import FacebookUser, FacebookPage, InstagramAccount

class FacebookUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = FacebookUser
        fields = ['id', 'username', 'facebook_id', 'created_at']

class FacebookPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookPage
        fields = ['id', 'page_id', 'page_name', 'webhook_subscribed', 'created_at', 'updated_at']

class InstagramAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramAccount
        fields = ['id', 'instagram_id', 'username', 'webhook_subscribed', 'created_at', 'updated_at']
