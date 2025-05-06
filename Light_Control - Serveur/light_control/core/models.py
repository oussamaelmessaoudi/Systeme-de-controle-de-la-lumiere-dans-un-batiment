from django.db import models
from django.contrib.auth.models import User
import json

class Zone(models.Model):
    name = models.CharField(max_length=100, null=True)
    description = models.TextField(blank=True, null=True)
    current_state = models.BooleanField(default=False)
    floor = models.IntegerField(null=True)
    building = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name} (Building: {self.building}, Floor: {self.floor})"
    
    def toggle_light(self, state):
        from rpc.client import RPCClient
        client = RPCClient()
        result = client.set_light_state(self.id, state)
        if result.get('success', False):
            self.current_state = state
            self.save()
            return True
        return False
    
    def get_state(self):
        from rpc.client import RPCClient
        client = RPCClient()
        result = client.get_light_state(self.id)
        if result.get('success', False):
            self.current_state = result.get('state', self.current_state)
            self.save()
        return self.current_state

class Schedule(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='schedules')
    start_time = models.TimeField()
    end_time = models.TimeField()
    days_of_week = models.CharField(max_length=7, default="0000000")  # Un caractère par jour (1=actif, 0=inactif)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Schedule for {self.zone.name}: {self.start_time} - {self.end_time}"
    
    def should_be_on(self, dt):
        """Vérifie si la lumière devrait être allumée à un moment donné"""
        if not self.is_active:
            return False
            
        # Vérifier les dates de validité
        if self.valid_from and dt.date() < self.valid_from:
            return False
        if self.valid_until and dt.date() > self.valid_until:
            return False
            
        # Vérifier le jour de la semaine
        day_index = dt.weekday()  # 0=Lundi, 6=Dimanche
        if self.days_of_week[day_index] != "1":
            return False
            
        # Vérifier l'heure
        current_time = dt.time()
        return self.start_time <= current_time <= self.end_time

class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='permissions')
    can_view = models.BooleanField(default=True)
    can_control = models.BooleanField(default=False)
    can_schedule = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'zone')
        
    def __str__(self):
        return f"Permission for {self.user.username} on {self.zone.name}"

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('ON', 'Light turned on'),
        ('OFF', 'Light turned off'),
        ('SCHEDULE', 'Schedule modified'),
        ('LOGIN', 'User login'),
        ('LOGOUT', 'User logout'),
        ('OTHER', 'Other action'),
    ]
    
    SOURCE_CHOICES = [
        ('MANUAL', 'Manual action'),
        ('SCHEDULE', 'Scheduled action'),
        ('SYSTEM', 'System action'),
        ('API', 'API action'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    details = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_action_display()} by {self.user or 'System'} at {self.timestamp}"
    
    @classmethod
    def record_activity(cls, action, source, user=None, zone=None, details=None):
        return cls.objects.create(
            user=user,
            zone=zone,
            action=action,
            source=source,
            details=details
        )