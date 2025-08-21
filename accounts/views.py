from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import FacebookUser, FacebookPage, InstagramAccount
from .utils import FacebookAPI
from .serializers import FacebookPageSerializer, InstagramAccountSerializer

# Additional views for accounts/views.py

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout the current user"""
    from django.contrib.auth import logout
    logout(request)
    return Response({'message': 'Logged out successfully'})
    
@api_view(['POST'])
@permission_classes([AllowAny])
def facebook_login(request):
    """Handle Facebook OAuth login"""
    access_token = request.data.get('access_token')
    print(f"Access Token: {access_token}")  # Debugging line to check access token
    
    if not access_token:
        return Response({'error': 'Access token required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get user info from Facebook
        user_info = FacebookAPI.get_user_info(access_token)
        facebook_id = user_info['id']
        name = user_info.get('name', '')
        email = user_info.get('email', '')
        
        # Get or create user
        try:
            facebook_user = FacebookUser.objects.get(facebook_id=facebook_id)
            user = facebook_user.user
        except FacebookUser.DoesNotExist:
            # Create new user
            username = f"fb_{facebook_id}"
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name.split(' ')[0] if name else '',
                last_name=' '.join(name.split(' ')[1:]) if name and len(name.split(' ')) > 1 else ''
            )
            facebook_user = FacebookUser.objects.create(
                user=user,
                facebook_id=facebook_id,
                access_token=access_token
            )
        
        # Update access token
        facebook_user.access_token = access_token
        facebook_user.save()
        
        # Login user
        login(request, user)
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'facebook_id': facebook_id
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_pages(request):
    """Get user's Facebook pages and Instagram accounts"""
    try:
        facebook_user = FacebookUser.objects.get(user=request.user)
        pages_data = FacebookAPI.get_user_pages(facebook_user.access_token)
        
        # Store/update pages
        for page_data in pages_data:
            page, created = FacebookPage.objects.get_or_create(
                facebook_user=facebook_user,
                page_id=page_data['id'],
                defaults={
                    'page_name': page_data['name'],
                    'page_access_token': page_data['access_token']
                }
            )
            if not created:
                page.page_name = page_data['name']
                page.page_access_token = page_data['access_token']
                page.save()
            
            # Handle Instagram business account if available
            if 'instagram_business_account' in page_data:
                ig_data = page_data['instagram_business_account']
                instagram_name = FacebookAPI.get_instagrame_name(ig_data['id'], facebook_user.access_token) if ig_data['id'] else None
                print(f"Instagram Name: {instagram_name}")  # Debugging line
                ig_account, created = InstagramAccount.objects.get_or_create(
                    facebook_user=facebook_user,
                    instagram_id=ig_data['id'],
                    defaults={
                        'username': instagram_name.get('name', ''),
                        'access_token': page_data['access_token']
                    }
                )
        
        # Return serialized data
        pages = FacebookPage.objects.filter(facebook_user=facebook_user)
        instagram_accounts = InstagramAccount.objects.filter(facebook_user=facebook_user)
        
        return Response({
            'pages': FacebookPageSerializer(pages, many=True).data,
            'instagram_accounts': InstagramAccountSerializer(instagram_accounts, many=True).data
        })
        
    except FacebookUser.DoesNotExist:
        return Response({'error': 'Facebook user not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_webhooks(request):
    """Subscribe to webhooks for selected pages"""
    page_id = request.data.get('page_id')
    
    try:
        facebook_user = FacebookUser.objects.get(user=request.user)
        page = FacebookPage.objects.get(facebook_user=facebook_user, page_id=page_id)
        
        # Subscribe to webhooks
        result = FacebookAPI.subscribe_page_webhooks(page.page_id, page.page_access_token)
        
        if result.get('success'):
            page.webhook_subscribed = True
            page.save()
            return Response({'message': 'Webhooks subscribed successfully'})
        else:
            return Response({'error': 'Failed to subscribe webhooks'}, status=status.HTTP_400_BAD_REQUEST)
            
    except (FacebookUser.DoesNotExist, FacebookPage.DoesNotExist):
        return Response({'error': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)