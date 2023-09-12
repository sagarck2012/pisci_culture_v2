import datetime

from django.db import models

from user_management.models import User


# Create your models here.
class Pond(models.Model):
    # pond_id = models.CharField(max_length=255, unique=True, auto_created=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    depth = models.FloatField(default=0.0,)
    area = models.FloatField(default=0.0,)
    active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(default=datetime.datetime.now(), null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='updated_by')
    updated_at = models.DateTimeField(default=datetime.datetime.now(), null=True)

