import datetime
import json

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pond_management.api.serializers import PondSerializer
from pond_management.models import Pond
from user_management.api.tokens import CustomJWTAuthentication
from utilities.jwt_user_check import jwt_user_get


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def createPond(request):
    try:
        data = jwt_user_get(request)
        user = data['user']
        json_data = json.loads(request.body)
        print(f'{user}')
        existing_pond = Pond.objects.filter(name=json_data['name'], user=user)

        if len(existing_pond) > 0:
            response = {
                "data": json_data,
                "message": "Pond with this name already exists."
            }
            return Response(response, status=status.HTTP_201_CREATED)

        pond_data = {
            'name': json_data['name'],
            'depth': json_data['depth'],
            'area': json_data['area'],
            'user': user,
            'created_by': user
        }
        pond = Pond(**pond_data)
        pond.save()
        serializer = PondSerializer(pond)

        if pond.id:
            response = {
                "data": serializer.data,
                "message": "Successfully Created."
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def editPond(request):
    try:
        data = jwt_user_get(request)
        user = data['user']
        json_data = json.loads(request.body)
        pond = Pond.objects.get(pk=json_data['id'])
        print(pond)
        if pond:
            pond.name = json_data['name']
            pond.area = json_data['area']
            pond.depth = json_data['depth']
            pond.updated_by = user
            pond.updated_at = datetime.datetime.now()
            pond.save()
            serializer = PondSerializer(pond)
            response = {
                "data": json_data,
                "message": "Pond does not exist."
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                "data": json_data,
                "message": "Pond does not exist."
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # pond_data = json_data
        # serializer = PondSerializer(data=pond_data, partial=True)
        #
        # if serializer.is_valid():
        #     serializer.save()

    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def deletePond(request, pk):
    try:
        pond = Pond.objects.get(id=pk)
        print(pond)
        if not pond:
            return Response({'error': 'Pond not found'}, status=status.HTTP_404_NOT_FOUND)
        pond.active = False
        pond.save()
        return Response({'message': 'Pond deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def listPond(request):
    try:
        data = jwt_user_get(request)
        user = data['user']
        pond = Pond.objects.filter(active=True, user_id=user.id)
        serializer = PondSerializer(pond, many=True)

        response = {
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
