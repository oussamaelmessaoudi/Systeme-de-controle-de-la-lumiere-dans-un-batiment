from django.contrib import admin
from .models import Zone, Permission, Schedule, ActivityLog


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'building', 'floor', 'current_state', 'created_at')
    list_filter = ('building', 'floor', 'current_state')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'zone', 'can_view', 'can_control', 'can_schedule', 'created_at')
    list_filter = ('can_view', 'can_control', 'can_schedule')
    search_fields = ('user__username', 'zone__name')
    ordering = ('user',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('zone', 'start_time', 'end_time', 'days_of_week', 'is_active', 'valid_from')
    list_filter = ('is_active', 'valid_from')
    search_fields = ('zone__name',)
    ordering = ('zone', 'start_time')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'zone', 'action', 'source', 'timestamp')
    list_filter = ('action', 'source', 'timestamp')
    search_fields = ('user__username', 'zone__name', 'details')
    ordering = ('-timestamp',)