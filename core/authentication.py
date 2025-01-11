from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import User
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import authenticate_request, AuthenticateRequestOptions
import os

class ClerkAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            sdk = Clerk(bearer_auth=os.getenv('CLERK_SECRET_KEY'))
            request_state = authenticate_request(
                sdk,
                request,
                AuthenticateRequestOptions(
                    authorized_parties=None  # Accept any issuer for simplicity
                )
            )

            if not request_state.is_signed_in:
                raise exceptions.AuthenticationFailed(request_state.reason)

            # Get or create user based on Clerk user ID
            user_id = request_state.payload.get('sub')
            user, _ = User.objects.get_or_create(
                username=user_id,
                defaults={
                    'email': request_state.payload.get('email', ''),
                    'is_active': True
                }
            )
            
            return (user, None)
            
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e)) 