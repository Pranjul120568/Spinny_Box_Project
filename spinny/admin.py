from django.contrib import admin
from .models import User, box, room
# Register your models here.


@admin.register(User)
class user_admin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email',
                    'password', 'mobile_no', 'is_staff']


@admin.register(room)
class room_admin(admin.ModelAdmin):
    list_display = ['average_area', 'average_volume', 'total_boxes'
                    ]


@admin.register(box)
class box_admin(admin.ModelAdmin):
    list_display = ['length', 'breadth', 'height',
                    'area', 'volume', 'creator', 'last_updated_by', 'last_updated_on', 'created_on', 'current_week']
