from rest_framework import viewsets
from core.models import Zone, Schedule, Permission, ActivityLog
from django.contrib.auth.models import User
from .serializers import UserSerializer, ZoneSerializer, ScheduleSerializer, PermissionSerializer, ActivityLogSerializer
from rest_framework.permissions import AllowAny
from core.models import Lamp
from rest_framework.views import APIView
from rest_framework.response import Response
import json

STATE_FILE = 'lamp_states.json'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [AllowAny]

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer

class LampStatusAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            with open(STATE_FILE, 'r') as f:
                states = json.load(f)
            data = [{"id": int(k), "status": v["status"]} for k, v in states.items()]
            return Response(data)
        except FileNotFoundError:
            return Response([], status=404)
        except json.JSONDecodeError:
            return Response([], status=500)