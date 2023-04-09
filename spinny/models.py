from django.db import models
from django.contrib.auth.models import AbstractUser
from .dates import get_week
import datetime
# Create your models here.


class User(AbstractUser):
    username = models.CharField(
        max_length=30, unique=True)
    email = models.EmailField(
        ('email address'), max_length=254, unique=True, null=True, blank=True)
    password = models.CharField(max_length=270)
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=('Designates whether the user can log into this admin site.'),
    )

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'


class box(models.Model):
    length = models.IntegerField()
    breadth = models.IntegerField()
    height = models.IntegerField()
    area = models.IntegerField()
    volume = models.IntegerField()
    creator = models.CharField(max_length=30,)
    last_updated_by = models.CharField(max_length=30)
    last_updated_on = models.DateField(default=datetime.date.today())
    created_on = models.DateField()
    current_week = models.IntegerField(default=get_week())


class room(models.Model):
    # Done in serializers
    # total_area = models.IntegerField()
    # total_volume = models.IntegerField()
    average_area = models.IntegerField()
    average_volume = models.IntegerField()
    total_boxes = models.IntegerField()
