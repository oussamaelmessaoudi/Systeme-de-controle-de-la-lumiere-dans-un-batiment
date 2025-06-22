from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django import forms
from .models import Zone, Permission, Schedule, ActivityLog
from rpc.client import LightController
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Schedule
from core.models import Analytics
from api.serializers import *
from django.db.models import Sum
from django.db.models.functions import TruncDate
from .models import Lamp
from rpc.client import LightController
from .models import Zone
from collections import defaultdict

# Décorateur personnalisé pour vérifier is_staff
def staff_member_required(view_func):
    """
    Décorateur qui vérifie si l'utilisateur est connecté et a is_staff=True.
    Redirige vers la page de connexion si la condition n'est pas remplie.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseRedirect(reverse('login'))
        return view_func(request, *args, **kwargs)
    return wrapper

# Formulaires
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff']

class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['user', 'zone', 'can_view', 'can_control', 'can_schedule']

class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['name', 'building', 'floor']

class ScheduleForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=[
            ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
            ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
        ],
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = Schedule
        fields = ['zone', 'start_time', 'end_time', 'action', 'days', 'is_active', 'valid_from', 'valid_until']
        widgets = {
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }




# Vues existantes
@login_required
def dashboard(request):
    permissions = Permission.objects.filter(user=request.user, can_view=True)
    zones = [perm.zone for perm in permissions]
    return render(request, 'core/dashboard.html', {'zones': zones})

def simulation_view(request):
    all_zones = Zone.objects.prefetch_related('lamps').order_by('name')

    context = {
        'zones': all_zones
    }
    return render(request, 'core/simulation.html', context)



       

@login_required
def toggle_lamp(request, lamp_id):
    lamp = get_object_or_404(Lamp, pk=lamp_id, user=request.user)

    controller = LightController()
    try:
        controller.toggle_lamp(lamp.id)
    except Exception as e:
        print(f"RPC call failed: {e}")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))



@login_required
def control_zone(request, zone_id):
    zone = get_object_or_404(Zone, pk=zone_id)

    if request.method == "POST":
        controller = LightController()
        action = request.POST.get("action")

        try:
            if action == "turn_on":
                controller.turn_on(zone.id)
                zone.current_state = True
                zone.save(update_fields=['current_state'])
                messages.success(request, f"Command to turn ON zone '{zone.name}' was sent.")

            elif action == "turn_off":
                controller.turn_off(zone.id)
                zone.current_state = False
                zone.save(update_fields=['current_state'])
                messages.success(request, f"Command to turn OFF zone '{zone.name}' was sent.")

        except Exception as e:
            print(f"RPC call failed: {e}")
            messages.error(request, "Failed to communicate with the control server.")

        return redirect('control_zone', zone_id=zone.id)

    return render(request, 'core/zone_detail.html', {'zone': zone})

# Vues pour la gestion admin
@staff_member_required
def manage_users(request):
    users = User.objects.all()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f"User {user.username} created successfully.")
            return redirect('manage_users')
    else:
        form = UserForm()
    return render(request, 'core/manage_users.html', {'users': users, 'form': form})

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, f"User {user.username} deleted successfully.")
        return redirect('manage_users')
    return render(request, 'core/confirm_delete.html', {'object': user, 'type': 'user'})

@staff_member_required
def manage_permissions(request):
    permissions = Permission.objects.all()
    if request.method == "POST":
        form = PermissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Permission created successfully.")
            return redirect('manage_permissions')
    else:
        form = PermissionForm()
    return render(request, 'core/manage_permissions.html', {'permissions': permissions, 'form': form})

@staff_member_required
def delete_permission(request, permission_id):
    permission = get_object_or_404(Permission, id=permission_id)
    if request.method == "POST":
        permission.delete()
        messages.success(request, "Permission deleted successfully.")
        return redirect('manage_permissions')
    return render(request, 'core/confirm_delete.html', {'object': permission, 'type': 'permission'})

@staff_member_required
def manage_zones(request):
    zones = Zone.objects.all()
    if request.method == "POST":
        form = ZoneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Zone created successfully.")
            return redirect('manage_zones')
    else:
        form = ZoneForm()
    return render(request, 'core/manage_zones.html', {'zones': zones, 'form': form})

@staff_member_required
def delete_zone(request, zone_id):
    zone = get_object_or_404(Zone, id=zone_id)
    if request.method == "POST":
        zone.delete()
        messages.success(request, "Zone deleted successfully.")
        return redirect('manage_zones')
    return render(request, 'core/confirm_delete.html', {'object': zone, 'type': 'zone'})

@staff_member_required
def manage_schedules(request):
    schedules = Schedule.objects.all()
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.days = ','.join(form.cleaned_data['days'])
            schedule.save()
            messages.success(request, "Schedule created successfully.")
            return redirect('manage_schedules')
    else:
        form = ScheduleForm()
    return render(request, 'core/manage_schedules.html', {'schedules': schedules, 'form': form})

@staff_member_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == "POST":
        schedule.delete()
        messages.success(request, "Schedule deleted successfully.")
        return redirect('manage_schedules')
    return render(request, 'core/confirm_delete.html', {'object': schedule, 'type': 'schedule'})

class PredictionView(APIView):
    def get(self, request, zone_id=None):
        if zone_id:
            schedules = Schedule.objects.filter(zone_id=zone_id, is_active=True)
        else:
            schedules = Schedule.objects.filter(is_active=True)
        serializer = PredictionSerializer(schedules, many=True)
        return Response(serializer.data)

def predictions_dashboard(request, zone_id):
    return render(request, 'core/predictions.html', {'zone_id': zone_id})

class UsageFrequencyView(APIView):
    def get(self, request):
        analytics = Analytics.objects.filter(metric_type='usage_frequency').values('metric_value')
        print(analytics.query)
        print(list(analytics))
        serializer = UsageFrequencySerializer(analytics, many=True)
        return Response(serializer.data)

class EnergyConsumptionView(APIView):
    def get(self, request):
        analytics = Analytics.objects.filter(metric_type='energy_consumption').annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            metric_value=Sum('metric_value')
        ).order_by('date')
        serializer = EnergyConsumptionSerializer(analytics, many=True)
        return Response(serializer.data)

def stats_dashboard(request):
    return render(request, 'core/stats.html')

class PredictionView(APIView):
    def get(self, request, zone_id):
        data = []  # Query core_schedule
        serializer = PredictionSerializer(data, many=True)
        return Response(serializer.data)


