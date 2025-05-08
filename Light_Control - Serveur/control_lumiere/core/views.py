from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Zone, Permission, ActivityLog
from rpc.client import LightController


@login_required
def dashboard(request):
    """Affiche le tableau de bord avec les zones accessibles."""
    user = request.user
    permissions = Permission.objects.filter(user=user, can_view=True)
    zones = [perm.zone for perm in permissions]
    return render(request, "core/dashboard.html", {"zones": zones})


@login_required
def control_zone(request, zone_id):
    """Contrôle une zone (allumer/éteindre)."""
    zone = get_object_or_404(Zone, id=zone_id)
    permission = get_object_or_404(Permission, user=request.user, zone=zone, can_control=True)
    
    controller = LightController()
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "turn_on":
                controller.turn_on(zone.id)
                zone.turn_on()
                ActivityLog.objects.create(
                    user=request.user,
                    zone=zone,
                    action="turn_on",
                    source="manual"
                )
            elif action == "turn_off":
                controller.turn_off(zone.id)
                zone.turn_off()
                ActivityLog.objects.create(
                    user=request.user,
                    zone=zone,
                    action="turn_off",
                    source="manual"
                )
            return redirect("dashboard")
        except Exception as e:
            ActivityLog.objects.create(
                user=request.user,
                zone=zone,
                action="error",
                source="manual",
                details=str(e)
            )
            return render(request, "core/zone_detail.html", {"zone": zone, "error": str(e)})
    return render(request, "core/zone_detail.html", {"zone": zone})