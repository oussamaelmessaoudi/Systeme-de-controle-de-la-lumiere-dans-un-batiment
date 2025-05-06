from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Zone, Schedule, Permission, ActivityLog
from .forms import ScheduleForm, UserProfileForm

@login_required
def dashboard(request):
    """
    Vue du tableau de bord principal
    """
    # Récupérer les zones accessibles par l'utilisateur
    if request.user.is_staff:
        zones = Zone.objects.all()
    else:
        zones = Zone.objects.filter(
            permissions__user=request.user,
            permissions__can_view=True
        ).distinct()
    
    # Statistiques de base
    zones_on = zones.filter(current_state=True).count()
    zones_off = zones.filter(current_state=False).count()
    
    # Récupérer les dernières activités
    if request.user.is_staff:
        recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:10]
    else:
        recent_activities = ActivityLog.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:10]
    
    context = {
        'zones_count': zones.count(),
        'zones_on': zones_on,
        'zones_off': zones_off,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def zone_list(request):
    """
    Liste des zones avec leur état
    """
    # Récupérer les zones accessibles par l'utilisateur
    if request.user.is_staff:
        zones = Zone.objects.all()
    else:
        zones = Zone.objects.filter(
            permissions__user=request.user,
            permissions__can_view=True
        ).distinct()
    
    # Ajout d'informations sur les permissions
    for zone in zones:
        if request.user.is_staff:
            zone.can_control = True
            zone.can_schedule = True
        else:
            try:
                permission = Permission.objects.get(user=request.user, zone=zone)
                zone.can_control = permission.can_control
                zone.can_schedule = permission.can_schedule
            except Permission.DoesNotExist:
                zone.can_control = False
                zone.can_schedule = False
    
    context = {
        'zones': zones,
    }
    
    return render(request, 'core/zone_list.html', context)

@login_required
def zone_detail(request, pk):
    """
    Détails d'une zone spécifique avec contrôles
    """
    zone = get_object_or_404(Zone, pk=pk)
    
    # Vérifier les permissions
    try:
        if not request.user.is_staff:
            permission = Permission.objects.get(user=request.user, zone=zone)
            if not permission.can_view:
                messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette zone.")
                return redirect('core:zone_list')
            can_control = permission.can_control
            can_schedule = permission.can_schedule
        else:
            can_control = True
            can_schedule = True
    except Permission.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette zone.")
            return redirect('core:zone_list')
        can_control = False
        can_schedule = False
    
    # Récupérer les programmations pour cette zone
    schedules = Schedule.objects.filter(zone=zone)
    
    # Récupérer les activités récentes pour cette zone
    recent_activities = ActivityLog.objects.filter(zone=zone).order_by('-timestamp')[:20]
    
    # Traiter l'action de contrôle si présente
    if request.method == 'POST' and can_control:
        action = request.POST.get('action')
        if action in ['turn_on', 'turn_off']:
            new_state = action == 'turn_on'
            success = zone.toggle_light(new_state)
            
            if success:
                ActivityLog.record_activity(
                    action='ON' if new_state else 'OFF',
                    source='MANUAL',
                    user=request.user,
                    zone=zone,
                    details=f"Light state changed to {'ON' if new_state else 'OFF'} via web interface"
                )
                messages.success(request, f"Lumière {'allumée' if new_state else 'éteinte'} avec succès.")
            else:
                messages.error(request, "Échec du changement d'état de la lumière.")
                
            return redirect('core:zone_detail', pk=zone.pk)
    
    context = {
        'zone': zone,
        'schedules': schedules,
        'recent_activities': recent_activities,
        'can_control': can_control,
        'can_schedule': can_schedule,
    }
    
    return render(request, 'core/zone_detail.html', context)

@login_required
def schedule_list(request):
    """
    Liste des programmations
    """
    # Récupérer les programmations accessibles par l'utilisateur
    if request.user.is_staff:
        schedules = Schedule.objects.all()
    else:
        schedules = Schedule.objects.filter(
            zone__permissions__user=request.user,
            zone__permissions__can_view=True
        ).distinct()
    
    paginator = Paginator(schedules, 15)  # 15 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'core/schedule_list.html', context)

@login_required
def schedule_create(request):
    """
    Création d'une nouvelle programmation
    """
    # Récupérer les zones où l'utilisateur peut programmer
    if request.user.is_staff:
        available_zones = Zone.objects.all()
    else:
        available_zones = Zone.objects.filter(
            permissions__user=request.user,
            permissions__can_schedule=True
        ).distinct()
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, available_zones=available_zones)
        if form.is_valid():
            schedule = form.save(commit=False)
            
            # Vérifier si l'utilisateur a le droit de programmer cette zone
            try:
                if not request.user.is_staff:
                    permission = Permission.objects.get(user=request.user, zone=schedule.zone)
                    if not permission.can_schedule:
                        messages.error(request, "Vous n'avez pas l'autorisation de programmer cette zone.")
                        return redirect('core:schedule_list')
            except Permission.DoesNotExist:
                if not request.user.is_staff:
                    messages.error(request, "Vous n'avez pas l'autorisation de programmer cette zone.")
                    return redirect('core:schedule_list')
            
            schedule.save()
            
            ActivityLog.record_activity(
                action='SCHEDULE',
                source='MANUAL',
                user=request.user,
                zone=schedule.zone,
                details="Programmation créée"
            )
            
            messages.success(request, "Programmation créée avec succès.")
            return redirect('core:schedule_list')
    else:
        form = ScheduleForm(available_zones=available_zones)
    
    context = {
        'form': form,
        'is_create': True,
    }
    
    return render(request, 'core/schedule_form.html', context)

@login_required
def schedule_edit(request, pk):
    """
    Modification d'une programmation existante
    """
    schedule = get_object_or_404(Schedule, pk=pk)
    
    # Vérifier les permissions
    try:
        if not request.user.is_staff:
            permission = Permission.objects.get(user=request.user, zone=schedule.zone)
            if not permission.can_schedule:
                messages.error(request, "Vous n'avez pas l'autorisation de modifier cette programmation.")
                return redirect('core:schedule_list')
    except Permission.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, "Vous n'avez pas l'autorisation de modifier cette programmation.")
            return redirect('core:schedule_list')
    
    # Récupérer les zones où l'utilisateur peut programmer
    if request.user.is_staff:
        available_zones = Zone.objects.all()
    else:
        available_zones = Zone.objects.filter(
            permissions__user=request.user,
            permissions__can_schedule=True
        ).distinct()
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule, available_zones=available_zones)
        if form.is_valid():
            updated_schedule = form.save()
            
            ActivityLog.record_activity(
                action='SCHEDULE',
                source='MANUAL',
                user=request.user,
                zone=updated_schedule.zone,
                details="Programmation modifiée"
            )
            
            messages.success(request, "Programmation modifiée avec succès.")
            return redirect('core:schedule_list')
    else:
        form = ScheduleForm(instance=schedule, available_zones=available_zones)
    
    context = {
        'form': form,
        'schedule': schedule,
        'is_create': False,
    }
    
    return render(request, 'core/schedule_form.html', context)

@login_required
def schedule_delete(request, pk):
    """
    Suppression d'une programmation
    """
    schedule = get_object_or_404(Schedule, pk=pk)
    
    # Vérifier les permissions
    try:
        if not request.user.is_staff:
            permission = Permission.objects.get(user=request.user, zone=schedule.zone)
            if not permission.can_schedule:
                messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette programmation.")
                return redirect('core:schedule_list')
    except Permission.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette programmation.")
            return redirect('core:schedule_list')
    
    if request.method == 'POST':
        zone = schedule.zone
        schedule.delete()
        
        ActivityLog.record_activity(
            action='SCHEDULE',
            source='MANUAL',
            user=request.user,
            zone=zone,
            details="Programmation supprimée"
        )
        
        messages.success(request, "Programmation supprimée avec succès.")
        return redirect('core:schedule_list')
    
    context = {
        'schedule': schedule,
    }
    
    return render(request, 'core/schedule_confirm_delete.html', context)

@login_required
def activity_log(request):
    """
    Journal des activités
    """
    # Filtrer par utilisateur si ce n'est pas un admin
    if request.user.is_staff:
        logs = ActivityLog.objects.all().order_by('-timestamp')
    else:
        # Pour les utilisateurs normaux, seulement afficher leurs propres logs
        # et ceux des zones qu'ils peuvent voir
        logs = ActivityLog.objects.filter(
            user=request.user
        ).order_by('-timestamp')
    
    # Filtres supplémentaires basés sur les paramètres GET
    zone_id = request.GET.get('zone')
    action_type = request.GET.get('action')
    source_type = request.GET.get('source')
    
    if zone_id:
        logs = logs.filter(zone_id=zone_id)
    if action_type:
        logs = logs.filter(action=action_type)
    if source_type:
        logs = logs.filter(source=source_type)
    
    # Pagination
    paginator = Paginator(logs, 30)  # 30 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Récupérer les filtres pour les options de filtre
    if request.user.is_staff:
        zones = Zone.objects.all()
    else:
        zones = Zone.objects.filter(
            permissions__user=request.user,
            permissions__can_view=True
        ).distinct()
    
    action_types = ActivityLog.ACTION_CHOICES
    source_types = ActivityLog.SOURCE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'zones': zones,
        'action_types': action_types,
        'source_types': source_types,
        'selected_zone': zone_id,
        'selected_action': action_type,
        'selected_source': source_type,
    }
    
    return render(request, 'core/activity_log.html', context)

@login_required
def user_profile(request):
    """
    Profil utilisateur
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('core:dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Récupérer les statistiques sur les activités de l'utilisateur
    activity_count = ActivityLog.objects.filter(user=request.user).count()
    
    # Récupérer les zones accessibles
    zones = Zone.objects.filter(
        permissions__user=request.user,
        permissions__can_view=True
    ).distinct()
    
    # Récupérer les permissions
    permissions = Permission.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'activity_count': activity_count,
        'zones_count': zones.count(),
        'permissions': permissions,
    }
    
    return render(request, 'core/user_profile.html', context)

# Les vues AJAX suivantes sont utilisées pour les mises à jour en temps réel
@login_required
def zone_state_update(request, pk):
    """
    Vue AJAX pour mettre à jour l'état d'une zone
    """
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        zone = get_object_or_404(Zone, pk=pk)
        
        # Vérifier les permissions
        try:
            if not request.user.is_staff:
                permission = Permission.objects.get(user=request.user, zone=zone)
                if not permission.can_control:
                    return JsonResponse({'success': False, 'error': "Permission denied"}, status=403)
        except Permission.DoesNotExist:
            if not request.user.is_staff:
                return JsonResponse({'success': False, 'error': "Permission denied"}, status=403)
        
        # Récupérer le nouvel état
        new_state = request.POST.get('state') == 'true'
        
        # Exécuter l'action
        success = zone.toggle_light(new_state)
        
        if success:
            ActivityLog.record_activity(
                action='ON' if new_state else 'OFF',
                source='MANUAL',
                user=request.user,
                zone=zone,
                details=f"Light state changed to {'ON' if new_state else 'OFF'} via AJAX"
            )
            return JsonResponse({'success': True, 'state': zone.current_state})
        else:
            return JsonResponse({'success': False, 'error': "Failed to change light state"}, status=500)
    
    return JsonResponse({'success': False, 'error': "Invalid request"}, status=400)

@login_required
def zone_states(request):
    """
    Vue AJAX pour récupérer l'état de toutes les zones accessibles
    """
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Récupérer les zones accessibles par l'utilisateur
        if request.user.is_staff:
            zones = Zone.objects.all()
        else:
            zones = Zone.objects.filter(
                permissions__user=request.user,
                permissions__can_view=True
            ).distinct()
        
        # Préparer la réponse
        states = {}
        for zone in zones:
            # Rafraîchir l'état depuis le contrôleur
            actual_state = zone.get_state()
            states[zone.id] = actual_state
        
        return JsonResponse({'success': True, 'states': states})
    
    return JsonResponse({'success': False, 'error': "Invalid request"}, status=400)