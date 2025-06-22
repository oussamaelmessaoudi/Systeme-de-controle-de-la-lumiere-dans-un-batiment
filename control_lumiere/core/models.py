from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Zone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    building = models.CharField(max_length=100)
    floor = models.IntegerField()
    current_state = models.BooleanField(default=False)  # True = On, False = Off
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.building}, Floor {self.floor})"

    def turn_on(self):
        self.current_state = True
        self.save()

    def turn_off(self):
        self.current_state = False
        self.save()

class Lamp(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='lamps')
    status = models.BooleanField(default=False)
    gpio_pin = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="أدخل رقم الدبوس فقط، مثلاً: 26."
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_control = models.BooleanField(default=False)
    can_schedule = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.zone.name}"

class Schedule(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    action = models.CharField(
        max_length=10,
        choices=[('turn_on', 'Turn On'), ('turn_off', 'Turn Off')],
        default='turn_on'
    )
    days = models.CharField(max_length=100, default='Mon')
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.zone.name} - {self.action} at {self.start_time}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, default='unknown')
    timestamp = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=20, default='system')
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} on {self.zone.name} at {self.timestamp}"

class Analytics(models.Model):
    zone_id = models.IntegerField(default=1)  # Add default
    metric_type = models.CharField(max_length=50)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_analytics'