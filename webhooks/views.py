import json
import hmac
import hashlib
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import WebhookEvent, ThankYouMessage
from .serializers import WebhookEventSerializer
from accounts.models import FacebookUser

@csrf_exempt
@require_http_methods(["GET", "POST"])
def facebook_webhook(request):
    """Handle Facebook webhook verification and events"""
    
    if request.method == 'GET':
        # Webhook verification
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if verify_token == settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
            return HttpResponse(challenge)
        else:
            return HttpResponse('Error, wrong validation token', status=403)
    
    elif request.method == 'POST':
        # Verify signature
        signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
        if not verify_webhook_signature(request.body, signature):
            return HttpResponse('Forbidden', status=403)
        
        # Process webhook event
        try:
            data = json.loads(request.body)
            process_webhook_event(data)
            return HttpResponse('OK')
        except Exception as e:
            print(f"Webhook processing error: {e}")
            return HttpResponse('Error', status=500)

def verify_webhook_signature(payload, signature):
    """Verify webhook signature"""
    expected_signature = 'sha256=' + hmac.new(
        settings.FACEBOOK_APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

def process_webhook_event(data):
    """Process incoming webhook event"""
    for entry in data.get('entry', []):
        page_id = entry.get('id')
        
        # Handle messaging events
        if 'messaging' in entry:
            for messaging_event in entry['messaging']:
                process_messaging_event(page_id, messaging_event)
        
        # Handle feed events (comments)
        if 'changes' in entry:
            for change in entry['changes']:
                if change.get('field') == 'feed':
                    process_feed_event(page_id, change.get('value', {}))

def process_messaging_event(page_id, messaging_event):
    """Process messaging event (messages)"""
    try:
        # Find the user who owns this page
        page = FacebookPage.objects.get(page_id=page_id)
        user = page.facebook_user.user
        
        # Create webhook event
        event = WebhookEvent.objects.create(
            user=user,
            event_type='message',
            platform='facebook',
            page_id=page_id,
            sender_id=messaging_event.get('sender', {}).get('id'),
            message_text=messaging_event.get('message', {}).get('text', ''),
            timestamp=timezone.now(),
            raw_data=messaging_event
        )
        
        # Create thank you message
        create_thank_you_message(event)
        
    except FacebookPage.DoesNotExist:
        print(f"Page {page_id} not found")
    except Exception as e:
        print(f"Error processing messaging event: {e}")

def process_feed_event(page_id, feed_data):
    """Process feed event (comments)"""
    try:
        # Find the user who owns this page
        page = FacebookPage.objects.get(page_id=page_id)
        user = page.facebook_user.user
        
        # Determine if it's a live comment
        is_live = feed_data.get('item') == 'comment' and 'live_video_id' in feed_data
        
        event = WebhookEvent.objects.create(
            user=user,
            event_type='live_comment' if is_live else 'comment',
            platform='facebook',
            page_id=page_id,
            sender_id=feed_data.get('sender_id'),
            comment_text=feed_data.get('message', ''),
            timestamp=timezone.now(),
            raw_data=feed_data
        )
        
        # Create thank you message
        create_thank_you_message(event)
        
    except FacebookPage.DoesNotExist:
        print(f"Page {page_id} not found")
    except Exception as e:
        print(f"Error processing feed event: {e}")

def create_thank_you_message(event):
    """Create appropriate thank you message"""
    thank_you_messages = {
        'message': "Thank you for your message! We appreciate you reaching out to us.",
        'comment': "Thank you for your comment! We value your engagement with our content.",
        'live_comment': "Thank you for joining our live stream and commenting! Your participation means a lot to us.",
    }
    
    message = thank_you_messages.get(event.event_type, "Thank you for your engagement!")
    
    ThankYouMessage.objects.create(
        webhook_event=event,
        message=message
    )
    
    event.thank_you_sent = True
    event.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_webhook_events(request):
    """Get webhook events for the authenticated user"""
    events = WebhookEvent.objects.filter(user=request.user)[:50]  # Last 50 events
    serializer = WebhookEventSerializer(events, many=True)
    return Response(serializer.data)