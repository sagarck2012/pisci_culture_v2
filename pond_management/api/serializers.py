from rest_framework import serializers

from pond_management.models import Pond


class PondSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pond
        fields = '__all__'
