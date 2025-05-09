from django.contrib import admin
from .models import Zone, Permission, Schedule, ActivityLog

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'floor', 'current_state', 'created_at', 'updated_at']
    list_filter = ['building', 'floor', 'created_at']
    search_fields = ['name', 'building', 'description']

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'zone', 'can_view', 'can_control', 'can_schedule', 'created_at', 'updated_at']
    list_filter = ['user', 'zone', 'can_view', 'can_control', 'can_schedule']
    search_fields = ['user__username', 'zone__name']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['zone', 'start_time', 'end_time', 'action', 'days', 'is_active', 'valid_from', 'valid_until', 'created_at', 'updated_at']
    list_filter = ['zone', 'action', 'is_active', 'valid_from']
    search_fields = ['zone__name']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'zone', 'action', 'timestamp', 'source']
    list_filter = ['action', 'source', 'timestamp']
    search_fields = ['user__username', 'zone__name', 'details']