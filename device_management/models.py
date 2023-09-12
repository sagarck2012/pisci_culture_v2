from datetime import datetime

from django.db import models

from pond_management.models import Pond
from user_management.models import User


# Create your models here.
class DeviceReg(models.Model):
    device_id = models.CharField(unique=True, max_length=255)
    device_code = models.CharField(max_length=255, null=True)
    installed_by = models.CharField(max_length=255, null=True, )
    installed_at = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)
    reg_date = models.DateTimeField(default=datetime.now)
    reg_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="reg_by")
    modify_date = models.DateTimeField(null=True)
    modify_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="modified_by")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", null=True)


class DeviceData(models.Model):
    device_reg = models.ForeignKey(DeviceReg, on_delete=models.CASCADE)
    d_id = models.IntegerField(null=True, blank=True)
    value = models.FloatField(default=0.00, null=True, )
    device_code = models.CharField(max_length=255, null=True, blank=True)
    sensor_name = models.CharField(max_length=255, null=True, blank=True)
    parameter_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now, null=True, blank=True)
    data_time = models.DateTimeField(null=True)
    obj_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    device_in = models.ForeignKey(Pond, on_delete=models.CASCADE, null=True, blank=True)


class Notification(models.Model):
    level = models.CharField(max_length=255, null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    seen_status = models.BooleanField(default=False)
    device_reg = models.ForeignKey(DeviceReg, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now, null=True)
    notification_at = models.DateTimeField(null=True)
    topic_value = models.FloatField(default=0.0, null=True, blank=True)


class Config(models.Model):
    device_reg = models.ForeignKey(DeviceReg, on_delete=models.CASCADE)
    interval_time = models.IntegerField(default=0, null=True)
    device_in = models.ForeignKey(Pond, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='config_created_by')
    config_updated_at = models.DateTimeField(default=datetime.now, null=True)
    config_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='config_updated_by')
