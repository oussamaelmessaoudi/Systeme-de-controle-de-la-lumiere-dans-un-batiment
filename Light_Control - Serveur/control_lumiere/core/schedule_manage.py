from django.utils import timezone
from .models import Schedule, Zone, ActivityLog
from rpc.client import LightController


class ScheduleManager:
    def __init__(self):
        self.controller = LightController()

    def check_schedules(self):
        """Vérifie toutes les programmations actives et exécute les actions nécessaires."""
        now = timezone.now()
        schedules = Schedule.objects.filter(is_active=True, valid_from__lte=now, valid_until__gte=now)

        for schedule in schedules:
            if self._should_execute(schedule):
                self._execute_schedule(schedule)

    def _should_execute(self, schedule):
        """Vérifie si une programmation doit être exécutée (logique simplifiée)."""
        # À implémenter : vérifier l'heure actuelle et les jours de la semaine
        # Pour cet exemple, retourne True si dans la plage horaire
        now = timezone.now().time()
        return schedule.start_time <= now <= schedule.end_time

    def _execute_schedule(self, schedule):
        """Exécute l'action de la programmation."""
        zone = schedule.zone
        try:
            if schedule.start_time <= timezone.now().time():
                self.controller.turn_on(zone.id)
                zone.turn_on()
                self._log_action(zone, "turn_on", "automatic")
            elif schedule.end_time <= timezone.now().time():
                self.controller.turn_off(zone.id)
                zone.turn_off()
                self._log_action(zone, "turn_off", "automatic")
        except Exception as e:
            self._log_action(zone, "error", "automatic", details=str(e))

    def _log_action(self, zone, action, source, details=""):
        """Enregistre une action dans le journal."""
        ActivityLog.objects.create(
            zone=zone,
            action=action,
            source=source,
            details=details
        )