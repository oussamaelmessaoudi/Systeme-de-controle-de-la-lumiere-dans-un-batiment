import time
import threading
import datetime
import os
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'light_control.settings')
django.setup()

from core.models import Schedule, Zone, ActivityLog
from rpc.client import RPCClient  # Ou rpc.grpc_client import GRPCClient

class ScheduleManager:
    def __init__(self, check_interval=60):
        """
        Initialise le gestionnaire de programmation.
        check_interval: intervalle en secondes pour vérifier les programmations
        """
        self.check_interval = check_interval
        self.rpc_client = RPCClient()  # Ou GRPCClient()
        self.running = False
        self.thread = None
    
    def start(self):
        """Démarre le thread de vérification des programmations"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        print("Schedule Manager started")
    
    def stop(self):
        """Arrête le thread de vérification"""
        if not self.running:
            return
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Schedule Manager stopped")
    
    def _run(self):
        """Boucle principale qui vérifie périodiquement les programmations"""
        while self.running:
            self.check_schedules()
            time.sleep(self.check_interval)
    
    def check_schedules(self):
        """
        Vérifie toutes les programmations actives et exécute
        les actions nécessaires
        """
        now = datetime.datetime.now()
        active_schedules = Schedule.objects.filter(is_active=True)
        
        # Grouper par zone pour éviter des actions conflictuelles
        zone_states = {}
        
        for schedule in active_schedules:
            should_be_on = schedule.should_be_on(now)
            zone_id = schedule.zone.id
            
            # Si cette zone n'a pas encore été traitée ou
            # si l'état calculé est "on", mettre à jour
            if zone_id not in zone_states or should_be_on:
                zone_states[zone_id] = should_be_on
        
        # Exécuter les actions pour chaque zone
        for zone_id, should_be_on in zone_states.items():
            try:
                zone = Zone.objects.get(id=zone_id)
                current_state = zone.current_state
                
                # Ne changer l'état que s'il est différent
                if current_state != should_be_on:
                    result = self.rpc_client.set_light_state(zone_id, should_be_on)
                    
                    if result.get('success', False):
                        # Mettre à jour l'état local et enregistrer dans les logs
                        zone.current_state = should_be_on
                        zone.save()
                        
                        ActivityLog.record_activity(
                            action='ON' if should_be_on else 'OFF',
                            source='SCHEDULE',
                            zone=zone,
                            details=f"Light state changed to {'ON' if should_be_on else 'OFF'} by scheduler"
                        )
                        
                        print(f"Zone {zone.name}: Light turned {'ON' if should_be_on else 'OFF'} by scheduler")
            except Zone.DoesNotExist:
                print(f"Zone {zone_id} not found")
            except Exception as e:
                print(f"Error setting state for zone {zone_id}: {e}")

# Pour exécuter le gestionnaire directement
if __name__ == "__main__":
    manager = ScheduleManager(check_interval=10)  # 10 secondes pour les tests
    try:
        manager.start()
        print("Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()