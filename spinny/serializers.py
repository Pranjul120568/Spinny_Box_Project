from rest_framework import serializers
from .models import User, box, room


class user_serializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'password', 'is_staff']


class room_serializers(serializers.ModelSerializer):
    class Meta:
        model = room
        fields = ['average_area', 'average_volume', 'total_boxes']


class box_serializers(serializers.ModelSerializer):
    class Meta:
        model = box
        fields = ['id', 'length', 'breadth', 'height',
                  'area', 'volume', 'creator', 'last_updated_by', 'last_updated_on', 'created_on', 'current_week']


class box_not_staff_serializers(serializers.ModelSerializer):
    class Meta:
        model = box
        fields = ['id', 'length', 'breadth', 'height',
                  'area', 'volume']
