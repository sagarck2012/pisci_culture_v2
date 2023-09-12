import jwt
from rest_framework import status
from rest_framework.response import Response

from pc_culture import settings
from user_management.models import User


def jwt_user_get(request):
    authorization_header = request.headers.get('Authorization')
    if authorization_header and authorization_header.startswith('Bearer '):
        token = authorization_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print(payload)
            user_id = payload['user_id']
            email = payload['email']
            user = User.objects.get(email=email)
            return {"user": user, "data": payload}
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
