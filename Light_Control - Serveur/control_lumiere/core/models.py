from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Zone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    floor = models.IntegerField()
    building = models.CharField(max_length=100)
    current_state = models.BooleanField(default=False)  # True: allumé, False: éteint
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def turn_on(self):
        self.current_state = True
        self.save()

    def turn_off(self):
        self.current_state = False
        self.save()


class Schedule(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="schedules")
    start_time = models.TimeField()
    end_time = models.TimeField()
    days_of_week = models.CharField(max_length=50)  # Ex. "1,2,3" pour lundi, mardi, mercredi
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.zone.name} - {self.start_time} to {self.end_time}"

    def is_due(self):
        # Logique pour vérifier si la programmation doit être exécutée
        # À implémenter selon les besoins (ex. vérifier l'heure et le jour)
        return False


class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="permissions")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="permissions")
    can_view = models.BooleanField(default=True)
    can_control = models.BooleanField(default=False)
    can_schedule = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.zone.name}"


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="activity_logs")
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, related_name="activity_logs")
    action = models.CharField(max_length=100)  # Ex. "turn_on", "turn_off", "schedule_created"
    source = models.CharField(max_length=50)  # Ex. "manual", "automatic"
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.zone.name} by {self.user.username} at {self.timestamp}"