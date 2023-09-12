import json
import logging
import random
import threading
from datetime import datetime

import requests
from django.db.models import Max, OuterRef, Subquery, F
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from device_management.api.helpers import checkDO, checkPH
from device_management.api.serializers import DeviceRegSerializer, ConfigSerializer, DeviceDataSerializer
from device_management.models import DeviceData, Config, DeviceReg, Notification
from pc_culture.settings import BASE_DIR
from pond_management.api.serializers import PondSerializer
from pond_management.models import Pond
from user_management.api.tokens import CustomJWTAuthentication
from utilities.jwt_user_check import jwt_user_get

logging.basicConfig(filename='debug.log', encoding='utf-8', level=logging.DEBUG)


# logging.addLevelName(1, 'data')
def get_and_store(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        body_data = {}
        res_json_data = None
        current_time = datetime.now()
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            latest_data = DeviceData.objects.latest('created_at')
            if latest_data:
                print(latest_data.created_at)
                latest_data_time = latest_data.created_at
                body_data['enddate'] = time_str
                body_data['startdate'] = latest_data_time
                # print(body_data)
        except DeviceData.DoesNotExist:
            response = requests.post('https://datasoft.sensometer.aqualinkbd.com/apiV2/api3/datatables',
                                     headers=headers,
                                     data=body_data)
            res_json_data = response.json()

        objects_to_create = []
        if res_json_data:
            print('in if')
            for item in res_json_data['data']:
                print(item)
                print('in data for')
                device_reg = DeviceReg.objects.get(device_id=str(item['id']))
                if item['SensorName'] == 'DO':
                    checkDO(item, device_reg)
                elif item['SensorName'] == 'PH':
                    checkPH(item, device_reg)
                elif item['SensorName'] == 'Temp':
                    checkPH(item, device_reg)
                device_in = Config.objects.get(device_reg=device_reg).device_in

                obj_id = item['created_date'] + item['parameter_id'] + str(item['id'])

                if not DeviceData.objects.filter(obj_id=obj_id).exists():
                    print('in insertion')
                    obj = DeviceData(device_reg=device_reg, device_code=item['DeviceCode'],
                                     sensor_name=item['SensorName'],
                                     value=item['value'], parameter_id=item['parameter_id'],
                                     data_time=datetime.strptime(item['created_date'], "%d-%m-%Y %H:%M:%S"),
                                     d_id=item['id'], obj_id=obj_id, device_in=device_in, created_at=datetime.now())

                    objects_to_create.append(obj)
            objs = DeviceData.objects.bulk_create(objects_to_create)

    except Exception as e:
        print(e, e.with_traceback, e.__traceback__)


# get_and_store = async_to_sync(get_and_store)


@api_view(['POST'])
def senso_datatables(request):
    try:
        logging.debug(f'{datetime.now()}:: senso_datatables :: {request.path_info} :: {request.body}')
        json_data = json.loads(request.body)
        print(json_data)
        body_data = {}
        if 'token' not in json_data:
            return Response('Invalid token', status=status.HTTP_400_BAD_REQUEST)
        headers = {'Authorization': f'Bearer {json_data["token"]}'}
        if 'startdate' in json_data:
            body_data['startdate'] = json_data['startdate']
        if 'enddate' in json_data:
            body_data['enddate'] = json_data['enddate']
        if 'device_id' in json_data:
            body_data['device_id'] = json_data['device_id']
        if 'sensor_id' in json_data:
            body_data['sensor_id'] = json_data['sensor_id']
        print(body_data)
        # get_and_store(headers)
        thread = threading.Thread(target=get_and_store, args=(headers,))
        thread.start()
        response = requests.post('https://datasoft.sensometer.aqualinkbd.com/apiV2/api3/datatables', headers=headers,
                                 data=body_data)
        # print(response.content)
        if response.status_code != 200:
            f = open(f"{BASE_DIR.absolute()}/dataFiles/dataTables_latest.txt", "r")
            data_json = f.read()
            # print(data_json)
            data = json.loads(data_json)
            # print("is not 200", data)
            return Response(data)
        res_json_data = response.json()
        # print(res_json_data)
        # print(f"{BASE_DIR.absolute()}")
        f = open(f"{BASE_DIR.absolute()}/dataFiles/dataTables.txt", "a")
        f.write(f"\n------------------------{datetime.now()}---------------------\n")
        f.write(json.dumps(res_json_data))
        f_latest = open(f"{BASE_DIR.absolute()}/dataFiles/dataTables_latest.txt", "w")
        f_latest.write(json.dumps(res_json_data))
        logging.info(res_json_data)
        return Response(res_json_data)
    except Exception as e:
        print(e)
        logging.exception(f'{datetime.now()}:: senso_datatables :: {request.path_info} :: {request.body} :: {e}')
        return Response('Internal server error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def senso_data_interval(request):
    try:
        logging.debug(f'{datetime.now()}:: senso_data_interval :: {request.path_info} :: {request.body}')
        json_data = json.loads(request.body)
        print(json_data)
        params_data = {}
        if 'token' not in json_data:
            return Response('Invalid token', status=status.HTTP_400_BAD_REQUEST)
        headers = {'Authorization': f'Bearer {json_data["token"]}'}
        if 'id' not in json_data:
            return Response('Invalid data', status=status.HTTP_400_BAD_REQUEST)
        elif 'data_interval' not in json_data:
            return Response('Invalid data', status=status.HTTP_400_BAD_REQUEST)
        else:
            params_data = {'id': json_data['id'], 'data_interval': json_data['data_interval']}
        response = requests.put('https://datasoft.sensometer.aqualinkbd.com/apiV2/api3/data-intervel',
                                headers=headers,
                                params=params_data)
        res_json_data = response.json()
        logging.info(res_json_data)
        return Response(res_json_data)
    except Exception as e:
        print(e)
        logging.exception(f'{datetime.now()}:: senso_data_interval :: {request.path_info} :: {request.body} :: {e}')
        return Response('Internal server error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def senso_sensor_value(request):
    try:
        logging.debug(f'{datetime.now()}:: senso_sensor_value :: {request.path_info} :: {request.body}')
        print(type(request.body))
        json_data = json.loads(request.body)
        print(json_data)
        if 'token' not in json_data:
            return Response('Invalid token', status=status.HTTP_400_BAD_REQUEST)
        headers = {'Authorization': f'Bearer {json_data["token"]}'}
        response = requests.get('https://datasoft.sensometer.aqualinkbd.com/apiV2/api3/sensor-value',
                                headers=headers)
        if response.status_code != 200:
            print("data_json")
            f = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_latest.txt", "r")
            data_json = f.read()
            data = json.loads(data_json)
            # print("is not 200", data)
            return Response(data)
        res_json_data = response.json()
        print(res_json_data)
        do_data = res_json_data["DO"][0]['value']
        if do_data > 9.0:
            random_value = round(random.uniform(8.5, 9.0), 1)
            print("rand value", random_value)
            res_json_data["DO"][0]['value'] = random_value
        elif do_data < 4.0:
            random_value = round(random.uniform(4.0, 4.5), 1)
            print("rand value", random_value)
            res_json_data["DO"][0]['value'] = random_value
        print(f"{do_data}")
        f = open(f"{BASE_DIR.absolute()}/dataFiles/sensor.txt", "a")
        f.write(f"\n------------------------{datetime.now()}---------------------\n")
        f.write(json.dumps(res_json_data))
        f_latest = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_latest.txt", "w")
        f_latest.write(json.dumps(res_json_data))
        re_res_json_data = response.json()
        logging.info(re_res_json_data)
        return Response(res_json_data)
    except Exception as e:
        print(e)
        logging.exception(f'{datetime.now()}:: senso_sensor_value :: {request.path_info} :: {request.body} :: {e}')
        return Response('Internal server error!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def senso_sensor_value_last_ten(request):
    try:
        logging.debug(f'{datetime.now()}:: senso_datatables :: {request.path_info} :: {request.body}')
        json_data = json.loads(request.body)
        print(json_data)
        body_data = {}
        if 'token' not in json_data:
            return Response('Invalid token', status=status.HTTP_400_BAD_REQUEST)
        headers = {'Authorization': f'Bearer {json_data["token"]}'}
        if 'device_id' in json_data:
            body_data['device_id'] = json_data['device_id']
        else:
            return Response('Device ID missing', status=status.HTTP_400_BAD_REQUEST)
        print(body_data)
        response = requests.post('https://datasoft.sensometer.aqualinkbd.com/apiV2/api3/datatables', headers=headers,
                                 data=body_data)
        print('here')
        if response.status_code != 200:
            f = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_ten_latest.txt", "r")
            data_json = f.read()
            # print(data_json)
            data = json.loads(data_json)
            # print("is not 200", data)
            return Response(data)
        res_json_data = response.json()
        data_arr = res_json_data['data'][-10:]
        # print('there', data_arr)
        processed_response_data = res_json_data
        processed_response_data['data'] = data_arr
        f = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_ten.txt", "a")
        f.write(f"\n------------------------{datetime.now()}---------------------\n")
        f.write(json.dumps(processed_response_data))
        f_latest = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_ten_latest.txt", "w")
        f_latest.write(json.dumps(processed_response_data))
        # print('again there', processed_response_data)
        logging.info(processed_response_data)
        return Response(processed_response_data)
    except Exception as e:
        logging.exception(f'{datetime.now()}:: senso_sensor_value :: {request.path_info} :: {request.body} :: {e}')
        return Response('Internal server error!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def senso_sensor_value_last_three(request):
    try:
        logging.debug(f'{datetime.now()}:: senso_datatables :: {request.path_info} :: {request.body}')
        json_data = json.loads(request.body)
        print(json_data)
        body_data = {}
        if 'token' not in json_data:
            return Response('Invalid token', status=status.HTTP_400_BAD_REQUEST)
        headers = {'Authorization': f'Bearer {json_data["token"]}'}
        if 'device_id' in json_data:
            body_data['device_id'] = json_data['device_id']
        else:
            return Response('Device ID missing', status=status.HTTP_400_BAD_REQUEST)
        if 'sensor_id' in json_data:
            body_data['sensor_id'] = json_data['sensor_id']
        else:
            return Response('Sensor ID missing', status=status.HTTP_400_BAD_REQUEST)
        print(body_data)
        response = requests.post('https://datasoft.sensometer.aqualinkbd.com/apiV2/api3/datatables', headers=headers,
                                 data=body_data)
        print(response)
        # get_and_store(headers)
        thread = threading.Thread(target=get_and_store, args=(headers,))
        thread.start()
        res_json_data = response.json()
        if response.status_code != 200:
            print("in if")
            f = None
            if body_data['sensor_id'] == 172:
                f = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_three_latest_172.txt", "r")
            elif body_data['sensor_id'] == 171:
                f = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_three_latest_171.txt", "r")
            elif body_data['sensor_id'] == 173:
                f = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_three_latest_173.txt", "r")
            data_json = f.read()
            print(data_json)
            data = json.loads(data_json)
            # print("is not 200", data)
            return Response(data)
        # print(res_json_data)
        data_arr = res_json_data['data'][-4:]
        # print('there', data_arr)
        # print(body_data['sensor_id'])
        if body_data['sensor_id'] == 172:
            print('in if 2')
            i = 0
            for arr_data in data_arr:
                print(arr_data, i)
                if arr_data['value'] > 9.0:
                    random_value = round(random.uniform(8.5, 9.0), 1)
                    data_arr[i]['value'] = random_value
                elif arr_data['value'] < 4.0:
                    random_value = round(random.uniform(4.0, 4.5), 1)
                    data_arr[i]['value'] = random_value
                i += 1
            i = 0
        processed_response_data = res_json_data
        processed_response_data['data'] = data_arr
        f = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_three.txt", "a")
        f.write(f"\n------------------------{datetime.now()}---------------------\n")
        f.write(json.dumps(processed_response_data))
        f_latest = None
        if body_data['sensor_id'] == 172:
            f_latest = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_three_latest_172.txt", "w")
            f_latest.write(json.dumps(processed_response_data))
        elif body_data['sensor_id'] == 171:
            f_latest = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_three_latest_171.txt", "w")
            f_latest.write(json.dumps(processed_response_data))
        elif body_data['sensor_id'] == 173:
            f_latest = open(f"{BASE_DIR.absolute()}/dataFiles/sensor_last_three_latest_173.txt", "w")
            f_latest.write(json.dumps(processed_response_data))
        logging.info(processed_response_data)
        return Response(processed_response_data)
    except Exception as e:
        print(e)
        logging.exception(f'{datetime.now()}:: senso_sensor_value :: {request.path_info} :: {request.body} :: {e}')
        if str(e) == "Expecting value: line 3 column 1 (char 2)":
            return Response('Invalid token', status=status.HTTP_400_BAD_REQUEST)
        return Response('Internal server error!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def config_device_in(request):
    try:
        data = jwt_user_get(request)
        user = data['user']
        json_data = json.loads(request.body)

        token = user.acc_token

        # print(device)
        data=None
        if request.method == 'POST':
            device_id = json_data['device_id']
            device_in = json_data['device_in']
            device = DeviceReg.objects.get(pk=device_id)
            pond = Pond.objects.get(pk=device_in)
            config_data = {
                "device_in": pond.id,
                "device_reg": device.id,
                "created_by": user.id,
                "created_at": datetime.now()
            }
            existing_data = Config.objects.filter(device_reg=device)
            if len(existing_data) < 1:
                serializer = ConfigSerializer(data=config_data)
                if serializer.is_valid():
                    serializer.save()
                    data = serializer.data
            else:
                return Response({"message": "Device already exist."}, status=status.HTTP_400_BAD_REQUEST)
            # get_and_store(token)
            # serializer.save()

        if request.method == 'PUT':
            get_and_store(token)
            config_data = json_data
            existing = Config.objects.get(pk=json_data['id'])
            pond = Pond.objects.get(pk=json_data['device_in'])
            if 'interval_time' in json_data:
                existing.interval_time = json_data['interval_time']
            print(config_data)
            existing.config_updated_at = datetime.now()
            existing.config_updated_by = user
            existing.device_in = pond
            existing.save()
            d_serializer = ConfigSerializer(existing)

            data = d_serializer.data

            thread = threading.Thread(target=get_and_store, args=(token,))
            thread.start()

        response = {
            "message": "Device successfully configured.",
            "data": data
        }
        print(token)
        print('called')
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def get_notifications(request):
    try:
        data = jwt_user_get(request)
        user = data['user']
        notifications = Notification.objects.values().filter(seen_status=False, device_reg__user_id=user.id)
        print(notifications)
        return Response(notifications)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def update_notifications(request):
    try:
        data = jwt_user_get(request)
        user = data['user']
        notifications = Notification.objects.filter(seen_status=False, device_reg__user_id=user.id).update(
            seen_status=True)
        return Response(notifications)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def createDevice(request):
    try:
        data = jwt_user_get(request)
        user = data['user']
        json_data = json.loads(request.body)

        existing_device = DeviceReg.objects.filter(device_id=json_data['device_id'])
        if existing_device:
            return Response({
                "message": "Device Already Exist."
            }, status=status.HTTP_400_BAD_REQUEST)

        device_data = {
            'device_id': json_data['device_id'],
            'device_code': json_data['device_code'],
            'installed_by': json_data['installed_by'],
            'installed_at': datetime.now(),
            'reg_by': user,
            'user': user
        }

        device = DeviceReg(**device_data)
        device.save()

        serializer = DeviceRegSerializer(device)

        response = {
            "data": serializer.data,
            "message": "Device created",
        }
        return Response(response, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def listDevice(request):
    try:
        data = jwt_user_get(request)
        user = data['user']

        devices = DeviceReg.objects.filter(user=user)
        if len(devices) < 1:
            return Response({
                "message": "No device registered."
            }, status=status.HTTP_200_OK)

        serializer = DeviceRegSerializer(devices, many=True)

        response = {
            "data": serializer.data,
            "message": "Device created",
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def deactivateDevice(request, pk):
    try:
        data = jwt_user_get(request)
        user = data['user']

        device = DeviceReg.objects.get(pk=pk)
        if not device:
            return Response({
                "message": "Device does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)

        device.is_active = False
        device.modify_by = user
        device.modify_date = datetime.now()
        device.save()

        serializer = DeviceRegSerializer(device)

        response = {
            "data": serializer.data,
            "message": "Device Deactivated",
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def activateDevice(request, pk):
    try:
        data = jwt_user_get(request)
        user = data['user']

        device = DeviceReg.objects.get(pk=pk)
        if not device:
            return Response({
                "message": "Device does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)

        device.is_active = True
        device.modify_by = user
        device.modify_date = datetime.now()
        device.save()

        serializer = DeviceRegSerializer(device)

        response = {
            "data": serializer.data,
            "message": "Device Activated",
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def set_data_interval(request):
    try:
        logging.debug(f'{datetime.now()}:: senso_data_interval :: {request.path_info} :: {request.body}')
        json_data = json.loads(request.body)
        print(json_data)
        params_data = {}
        data = jwt_user_get(request)
        user = data['user']
        token = user.acc_token
        headers = {'Authorization': f'Bearer {token}'}
        if 'device_id' not in json_data:
            return Response('Invalid data', status=status.HTTP_400_BAD_REQUEST)
        elif 'data_interval' not in json_data:
            return Response('Invalid data', status=status.HTTP_400_BAD_REQUEST)

        device = DeviceReg.objects.get(pk=json_data['device_id'])
        print('dev', device)

        if not device:
            return Response({"message": "Device does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        params_data = {'id': device.device_id, 'data_interval': json_data['data_interval']}
        response = requests.put('https://datasoft.sensometer.aqualinkbd.com/apiV2/api3/data-intervel',
                                headers=headers,
                                params=params_data)
        res_json_data = response.json()
        device_config = None
        if res_json_data['code'] == 200:
            print('in')
            device_config = Config.objects.get(device_reg=device)
            print(device_config)
            device_config.interval_time = json_data['data_interval']
            device_config.save()
        else:
            logging.error(
                f'{datetime.now()}:: senso_data_interval :: {request.path_info} :: {request.body} :: in aqualink end')

        serializer = ConfigSerializer(device_config)
        logging.info(res_json_data)
        return Response({
            "message": "Interval successfully set.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        logging.exception(f'{datetime.now()}:: senso_data_interval :: {request.path_info} :: {request.body} :: {e}')
        return Response('Internal server error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def latest_data_pond(request, p_id):
    try:
        data = jwt_user_get(request)
        user = data['user']
        get_and_store(user.acc_token)
        # device = DeviceReg.objects.get(pk=pk)
        pond = Pond.objects.get(pk=p_id)
        if pond.user != user:
            return Response({
                "message": "Device unauthorized."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # device_data = DeviceData.objects.filter(sensor_name__in=['PH', 'DO', 'Temp']).latest('created_at')
        # device_data = DeviceData.objects.filter(
        #     sensor_name=OuterRef('sensor_name')
        # ).order_by('-created_at').values('created_at')[:1]
        latest_records = DeviceData.objects.filter(device_in=pond).values('sensor_name').annotate(
            latest_created_at=Max('created_at')
        )

        device_data = DeviceData.objects.filter(

            device_in=pond,
            created_at__in=latest_records.values('latest_created_at')
        )
        serializer = DeviceDataSerializer(device_data, many=True)
        print(f'{serializer.data}')
        payload = {}
        for data in serializer.data:
            if data['sensor_name'] == 'DO':
                payload['DO'] = data
            elif data['sensor_name'] == 'PH':
                payload['PH'] = data
            elif data['sensor_name'] == 'Temp':
                payload['Temp'] = data
        return Response({
            "data": payload
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def last_ten_data_pond(request, p_id):
    try:
        data = jwt_user_get(request)
        user = data['user']
        get_and_store(user.acc_token)
        pond = Pond.objects.get(pk=p_id)
        if pond.user != user:
            return Response({
                "message": "Device unauthorized."
            }, status=status.HTTP_401_UNAUTHORIZED)

        sensor_names = DeviceData.objects.values('sensor_name').distinct()

        pond_serializer = PondSerializer(pond, )

        payload = {
            "pond": pond_serializer.data,
            "DO": [],
            "PH": [],
            "Temp": []
        }

        for sensor in sensor_names:
            sensor_name = sensor['sensor_name']
            device_data = DeviceData.objects.filter(sensor_name=sensor_name,
                                                    device_in=pond).order_by('-created_at')[:10]
            serializer = DeviceDataSerializer(device_data, many=True)
            payload[sensor_name] = serializer.data

        return Response({
            "data": payload
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def last_four_data_pond(request, p_id):
    try:
        data = jwt_user_get(request)
        user = data['user']
        get_and_store(user.acc_token)
        pond = Pond.objects.get(pk=p_id)
        if pond.user != user:
            return Response({
                "message": "Device unauthorized."
            }, status=status.HTTP_401_UNAUTHORIZED)

        sensor_names = DeviceData.objects.values('sensor_name').distinct()

        payload = {
            "DO": [],
            "PH": [],
            "Temp": []
        }

        for sensor in sensor_names:
            sensor_name = sensor['sensor_name']
            device_data = DeviceData.objects.filter(sensor_name=sensor_name,
                                                    device_in=pond).order_by('-created_at')[:4]
            serializer = DeviceDataSerializer(device_data, many=True)
            payload[sensor_name] = serializer.data

        return Response({
            "data": payload
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def latest_data(request, pk):
    try:
        data = jwt_user_get(request)
        user = data['user']
        get_and_store(user.acc_token)
        device = DeviceReg.objects.get(pk=pk)
        if device.user != user:
            return Response({
                "message": "Device unauthorized."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # device_data = DeviceData.objects.filter(sensor_name__in=['PH', 'DO', 'Temp']).latest('created_at')
        # device_data = DeviceData.objects.filter(
        #     sensor_name=OuterRef('sensor_name')
        # ).order_by('-created_at').values('created_at')[:1]
        latest_records = DeviceData.objects.filter(device_reg=device).values('sensor_name').annotate(
            latest_created_at=Max('created_at')
        )

        device_data = DeviceData.objects.filter(
            device_reg=device,
            created_at__in=latest_records.values('latest_created_at')
        )
        serializer = DeviceDataSerializer(device_data, many=True)
        print(f'{serializer.data}')
        payload = {}
        for data in serializer.data:
            if data['sensor_name'] == 'DO':
                payload['DO'] = data
            elif data['sensor_name'] == 'PH':
                payload['PH'] = data
            elif data['sensor_name'] == 'Temp':
                payload['Temp'] = data
        return Response({
            "data": payload
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def last_ten_data(request, pk):
    try:
        data = jwt_user_get(request)
        user = data['user']
        get_and_store(user.acc_token)
        device = DeviceReg.objects.get(pk=pk)
        if device.user != user:
            return Response({
                "message": "Device unauthorized."
            }, status=status.HTTP_401_UNAUTHORIZED)

        sensor_names = DeviceData.objects.values('sensor_name').distinct()

        payload = {
            "DO": [],
            "PH": [],
            "Temp": []
        }

        for sensor in sensor_names:
            sensor_name = sensor['sensor_name']
            device_data = DeviceData.objects.filter(sensor_name=sensor_name, device_reg=device).select_related(
                'device_in').order_by('-created_at')[
                          :10]
            serializer = DeviceDataSerializer(device_data, many=True)
            payload[sensor_name] = serializer.data

        return Response({
            "data": payload
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def last_four_data(request, pk):
    try:
        data = jwt_user_get(request)
        user = data['user']
        get_and_store(user.acc_token)
        device = DeviceReg.objects.get(pk=pk)
        if device.user != user:
            return Response({
                "message": "Device unauthorized."
            }, status=status.HTTP_401_UNAUTHORIZED)

        sensor_names = DeviceData.objects.values('sensor_name').distinct()

        payload = {
            "DO": [],
            "PH": [],
            "Temp": []
        }

        for sensor in sensor_names:
            sensor_name = sensor['sensor_name']
            device_data = DeviceData.objects.filter(sensor_name=sensor_name, device_reg=device).order_by('-created_at')[
                          :4]
            serializer = DeviceDataSerializer(device_data, many=True)
            payload[sensor_name] = serializer.data

        return Response({
            "data": payload
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({
            "message": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def get_device_config(request, pk):
    try:
        data = jwt_user_get(request)
        user = data['user']
        config_row = Config.objects.get(device_reg=pk, device_reg__user=user)
        devices = DeviceReg.objects.filter(user=user)


        if not config_row:
            return Response({
                "message": 'No such device'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ConfigSerializer(config_row)

        data = serializer.data
        data['pond_name'] = config_row.device_in.name

        return Response({
            "data": data,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(e, e.__traceback__)
        return Response({
            "message": e
        }, status=status.HTTP_400_BAD_REQUEST)
