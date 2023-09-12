from rest_framework import serializers

from device_management.models import DeviceReg, Config, DeviceData
from pond_management.api.serializers import PondSerializer


class DeviceRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceReg
        fields = '__all__'


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = '__all__'


class DeviceDataSerializer(serializers.ModelSerializer):
    # device_in = PondSerializer()

    class Meta:
        model = DeviceData
        # fields = '__all__'
        exclude = ('id', )
