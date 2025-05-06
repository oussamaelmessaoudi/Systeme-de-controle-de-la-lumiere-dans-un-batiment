from rest_framework import serializers
from core.models import Zone, Schedule, Permission, ActivityLog
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_active', 'date_joined']

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name', 'description', 'current_state', 'floor', 'building', 'created_at', 'updated_at']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'zone', 'start_time', 'end_time', 'days_of_week', 'is_active', 
                 'valid_from', 'valid_until', 'created_at', 'updated_at']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'user', 'zone', 'can_view', 'can_control', 'can_schedule']

class ActivityLogSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    zone_name = serializers.ReadOnlyField(source='zone.name')
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_username', 'zone', 'zone_name', 'timestamp', 
                 'action', 'source', 'details']