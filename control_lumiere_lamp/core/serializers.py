# core/serializers.py
from rest_framework import serializers
from core.models import Schedule

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['zone_id', 'start_time', 'end_time', 'action', 'days', 'valid_from']