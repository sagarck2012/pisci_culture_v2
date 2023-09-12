from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

from user_management.models import BlacklistedAccessToken


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user, token = super().authenticate(request)

        if BlacklistedAccessToken.objects.filter(token=token).exists():
            raise exceptions.AuthenticationFailed('Please Login')

        return user, token
