from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=50, unique=True, )
    name = models.CharField(max_length=255, null=True, blank=True)
    # date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    approve_status = models.IntegerField(default=0)
    # user_image = models.FileField(upload_to="uploads/", blank=True, null=True)
    # role = models.ForeignKey(Role, default=1, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=datetime.now)
    create_by = models.IntegerField(blank=True, null=True)
    modify_date = models.DateTimeField(null=True, blank=True)
    modify_by = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=11, unique=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    acc_token = models.CharField(max_length=255, null=True, blank=True)

    objects = UserManager()

    REQUIRED_FIELDS = ['username', 'is_admin']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        db_table = "user"


class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def blacklist(cls, token):
        cls.objects.create(token=token)

