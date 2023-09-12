import json
from datetime import datetime

import requests
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status as status_r, status

from device_management.api.views import get_and_store
from user_management.api.tokens import CustomJWTAuthentication
from user_management.models import User, BlacklistedAccessToken
import logging

logging.basicConfig(filename='debug.log', encoding='utf-8', level=logging.DEBUG)


def get_acc_token(user_email, user_pass):
    try:
        print('------', user_email, user_pass)
        form_data = {'user_email': user_email, 'user_pass': user_pass}
        response = requests.post('https://datasoft.sensometer.aqualinkbd.com/api/login', data=form_data)
        json_data = response.json()
        print(response.json())
        token = json_data['data']['token']
        user = User.objects.filter(email=user_email, ).update(acc_token=token)
        get_and_store(token)
    except Exception as e:
        print(e)
    # return response.json()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # password = ""

    def validate(self, attrs):
        # implement your logic here
        # print(type(attrs), attrs['username'], attrs['password'], )
        email = attrs['email']
        password = attrs['password']
        try:
            user = authenticate(email=email, password=password)
            get_acc_token(email, password)
        except Exception as e:
            print(e)
        # if not user:
        #     raise AuthenticationFailed('No such user')
        # print(type(user_acc))
        #     password_sb = base64.b64decode(password)
        #     password_s = password_sb.decode("ascii")
        #     # print(password_s)
        # attrs['password'] = password
        data = super().validate(attrs)
        return data

    # def __setattr__ (self, key, value):
    #     # print(self.data, self.initial_data)
    #     print(f'key=={key}::value=={value}::')
    #     # print(value[1])
    # def __getattr__(self, item):
    #     print(item.initial_data)

    @classmethod
    def get_token(cls, user):
        try:
            token = super().get_token(user)

            # Add custom claims
            token['username'] = user.username
            token['user_id'] = user.id
            token['name'] = user.name
            token['is_staff'] = user.is_staff
            token['email'] = user.email
            token['phone'] = user.phone
            # token['organization'] = user.organization
            # ...
            # user_acc = get_acc_token(user.email, cls.password)
            # print(user_acc)
            return token
        except Exception as e:
            print(e)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def create_user(request):
    status = None
    message = ''
    user = {}
    body_data = json.loads(request.body)
    password1 = body_data['password1']
    password2 = body_data['password2']
    if password1 != password2:
        status = status_r.HTTP_400_BAD_REQUEST
        message = 'Password did not match.'
        return Response({"message":message}, status)
    try:
        user = User.objects.create(
            username=body_data['username'],
            email=body_data['email'],
            phone=body_data['phone'],
            # password=setbody_data['password2'],
            # is_admin=False,
            name=body_data['name'],
        )
        user.set_password(body_data['password2'])
        user.save()
        user = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username
        }
        status = status_r.HTTP_201_CREATED
        message = 'User created successfully.'
    except Exception as e:
        print(e)
        status = status_r.HTTP_400_BAD_REQUEST
        message = 'User exists with given credential'
        return Response(json.dumps(message), status)
    context = {
        'message': message,
        'user': user,
    }
    return Response(context, status)


@api_view(['POST'])
def senso_login(request):
    try:
        logging.debug(f'{datetime.now()}::senso_login :: {request.path_info} :: {request.body}')
        print(request.body)
        json_data = json.loads(request.body)
        print(json_data)
        form_data = {'user_email': json_data['user_email'], 'user_pass': json_data['user_pass']}
        # form_data = request.body
        response = requests.post('https://datasoft.sensometer.aqualinkbd.com/api/login', data=form_data)
        json_data = response.json()
        return Response(json_data)
    except Exception as e:
        print(e)
        logging.exception(f'{datetime.now()}::senso_login :: {request.path_info} :: {request.body} :: {e}')
        return Response('Internal server error', status=status_r.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def senso_logout(request):
    try:
        print(request.headers)
        # json_headers = json.loads(request.headers)
        # print(json_headers)
        # return
        json_data = json.loads(request.body)
        if 'token' not in json_data:
            return Response('Invalid token', status=status_r.HTTP_400_BAD_REQUEST)
        headers = {'Authorization': f'Bearer {json_data["token"]}'}
        response = requests.post('https://datasoft.sensometer.aqualinkbd.com/api/logout', headers=headers)
        print('in logout')

        json_data = response.json()
        print(json_data)
        return Response(json_data)
    except Exception as e:
        print(e)
        return Response('Internal server error', status=status_r.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def logout(request):
    try:
        json_data = json.loads(request.body)
        refresh_token = json_data["refresh_token"]
        print(refresh_token)
        token = RefreshToken(refresh_token)
        token.blacklist()
        print('aa',token.access_token)
        authorization_header = request.headers.get('Authorization')
        token2 = authorization_header.split(' ')[1]
        print('aa', token2)
        BlacklistedAccessToken.blacklist(token2)
        # access_token = token.access_token
        # BlacklistedAccessToken.blacklist(access_token)

        return Response({"message": "Logged Out"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        print(e)
        return Response({"message": "Please login."}, status=status.HTTP_401_UNAUTHORIZED)
