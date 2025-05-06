from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Zone, Schedule, Permission, ActivityLog
from django.contrib.auth.models import User
from .serializers import (
    UserSerializer, ZoneSerializer, ScheduleSerializer,
    PermissionSerializer, ActivityLogSerializer
)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée: lecture pour tous, 
    modification uniquement pour les admin
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les zones selon les permissions de l'utilisateur"""
        user = self.request.user
        if user.is_staff:
            return Zone.objects.all()
        
        # Récupérer les zones où l'utilisateur a au moins la permission de voir
        return Zone.objects.filter(permissions__user=user, permissions__can_view=True).distinct()
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Endpoint pour allumer/éteindre une lumière"""
        zone = self.get_object()
        state = request.data.get('state')
        
        # Vérifier la permission
        try:
            permission = Permission.objects.get(user=request.user, zone=zone)
            if not permission.can_control:
                return Response({"error": "You don't have permission to control this zone"},
                                status=status.HTTP_403_FORBIDDEN)
        except Permission.DoesNotExist:
            return Response({"error": "You don't have permission to access this zone"},
                           status=status.HTTP_403_FORBIDDEN)
        
        # Exécuter l'action
        success = zone.toggle_light(state)
        
        if success:
            # Enregistrer dans les logs
            ActivityLog.record_activity(
                action='ON' if state else 'OFF',
                source='MANUAL',
                user=request.user,
                zone=zone,
                details=f"Light state changed to {'ON' if state else 'OFF'} via API"
            )
            return Response({"status": "success", "state": zone.current_state})
        else:
            return Response({"status": "error", "message": "Failed to change light state"},
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les programmations selon les permissions de l'utilisateur"""
        user = self.request.user
        if user.is_staff:
            return Schedule.objects.all()
        
        # Récupérer les programmations des zones accessibles
        return Schedule.objects.filter(
            zone__permissions__user=user,
            zone__permissions__can_view=True
        ).distinct()
    
    def perform_create(self, serializer):
        """Vérifie les permissions avant de créer une programmation"""
        zone = serializer.validated_data['zone']
        user = self.request.user
        
        if user.is_staff:
            serializer.save()
            ActivityLog.record_activity(
                action='SCHEDULE',
                source='MANUAL',
                user=user,
                zone=zone,
                details="Schedule created"
            )
            return
        
        try:
            permission = Permission.objects.get(user=user, zone=zone)
            if permission.can_schedule:
                serializer.save()
                ActivityLog.record_activity(
                    action='SCHEDULE',
                    source='MANUAL',
                    user=user,
                    zone=zone,
                    details="Schedule created"
                )
            else:
                self.permission_denied(self.request, message="You don't have permission to schedule this zone")
        except Permission.DoesNotExist:
            self.permission_denied(self.request, message="You don't have permission to access this zone")

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminOrReadOnly]

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all().order_by('-timestamp')
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les logs selon l'utilisateur"""
        user = self.request.user
        if user.is_staff:
            return ActivityLog.objects.all().order_by('-timestamp')
        
        # Pour les utilisateurs normaux, seulement leurs propres logs
        # et ceux des zones qu'ils peuvent voir
        return ActivityLog.objects.filter(
            user=user
        ).order_by('-timestamp')