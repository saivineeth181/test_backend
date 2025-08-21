import requests
from django.conf import settings
from typing import Dict, List, Optional

class FacebookAPI:
    BASE_URL = "https://graph.facebook.com/v23.0"
    
    @staticmethod
    def exchange_code_for_token(code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access token"""
        url = f"{FacebookAPI.BASE_URL}/oauth/access_token"
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'redirect_uri': redirect_uri,
            'code': code,
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    @staticmethod
    def get_user_info(access_token: str) -> Dict:
        """Get user information"""
        url = f"{FacebookAPI.BASE_URL}/me"
        params = {
            'access_token': access_token,
            'fields': 'id,name,email'
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    @staticmethod
    def get_user_pages(access_token: str) -> List[Dict]:
        """Get user's managed pages"""
        url = f"{FacebookAPI.BASE_URL}/me/accounts"
        params = {
            'access_token': access_token,
            'fields': 'id,name,access_token,instagram_business_account'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('data', [])
    
    @staticmethod
    def get_instagrame_name(instagram_id: str, page_access_token: str) -> Dict:
        """Subscribe page to webhooks"""
        url = f"{FacebookAPI.BASE_URL}/{instagram_id}"
        print(url)
        params = {
            'access_token': page_access_token,
            'fields': 'id,name'
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    @staticmethod
    def subscribe_page_webhooks(page_id: str, page_access_token: str) -> Dict:
        """Subscribe page to webhooks"""
        url = f"{FacebookAPI.BASE_URL}/{page_id}/subscribed_apps"
        params = {
            'access_token': page_access_token,
            'subscribed_fields': 'messages,messaging_postbacks,messaging_optins,message_deliveries,message_reads,messaging_payments,messaging_pre_checkouts,messaging_checkout_updates,messaging_account_linking,messaging_referrals,feed,mention,name,picture,category,description,conversations,branded_camera,message_mention,messaging_handovers,messaging_policy_enforcement,message_reactions,inbox_labels,standby,messages,messaging_postbacks,messaging_optins,message_deliveries,message_reads'
        }
        
        response = requests.post(url, params=params)
        return response.json()