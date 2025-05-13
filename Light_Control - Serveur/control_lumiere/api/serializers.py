from rest_framework import serializers
from core.models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ["id", "name", "description", "floor", "building", "current_state"]


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["id", "zone", "start_time", "end_time", "days_of_week", "is_active", "valid_from", "valid_until"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "user", "zone", "can_view", "can_control", "can_schedule"]


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ["id", "user", "zone", "action", "source", "details", "timestamp"]
    
class UsageFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = ['metric_value']

class EnergyConsumptionSerializer(serializers.Serializer):
    date = serializers.DateField()
    metric_value = serializers.FloatField()

class PredictionSerializer(serializers.Serializer):
    zone_id = serializers.IntegerField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    action = serializers.CharField(max_length=50)
    days = serializers.CharField(max_length=100)
    valid_from = serializers.DateField()