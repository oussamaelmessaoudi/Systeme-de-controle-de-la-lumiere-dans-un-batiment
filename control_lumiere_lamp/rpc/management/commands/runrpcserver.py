from django.core.management.base import BaseCommand
from xmlrpc.server import SimpleXMLRPCServer
import json
from core.models import Lamp

STATE_FILE = 'lamp_states.json'

def write_states_to_file():
    """Lit toutes les instances de la base de données et les écrit dans un fichier JSON."""
    lamps = Lamp.objects.all().order_by('id')
    # Convertir les données du modèle en un dictionnaire simple
    states = {lamp.id: {"status": lamp.status, "name": lamp.name} for lamp in lamps}
    with open(STATE_FILE, 'w') as f:
        json.dump(states, f)
    print(f"STATE-FILE: Updated '{STATE_FILE}' with current lamp states.")

class LightControlRPC:
    def turn_on(self, zone_id):
        """Allume toutes les lumières dans une zone spécifique."""
        print(f"RPC-SERVER: Received command to turn ON zone {zone_id}")
        # Nous mettons à jour toutes les lampes de la base de données en même temps.
        Lamp.objects.filter(zone_id=zone_id).update(status=True)
        #Nous mettons à jour le fichier d'état
        write_states_to_file()
        return True

    def turn_off(self, zone_id):
        """Éteint toutes les lumières dans une zone spécifique"""
        print(f"RPC-SERVER: Received command to turn OFF zone {zone_id}")
        Lamp.objects.filter(zone_id=zone_id).update(status=False)
        write_states_to_file()
        return True

    def toggle_lamp(self, lamp_id):
        """Modifie l'état d'une seule lampe"""
        print(f"RPC-SERVER: Received command to toggle lamp {lamp_id}")
        try:
            lamp = Lamp.objects.get(pk=lamp_id)
            lamp.status = not lamp.status
            lamp.save(update_fields=['status'])
            write_states_to_file()
            return True
        except Lamp.DoesNotExist:
            return False

class Command(BaseCommand):
    help = 'Runs the XML-RPC server and manages the state file.'

    def handle(self, *args, **options):
        # Nous écrivons l'état initial au démarrage
        print("Initializing state file...")
        write_states_to_file()

        server = SimpleXMLRPCServer(("localhost", 8001), allow_none=True)
        server.register_instance(LightControlRPC())
        self.stdout.write(self.style.SUCCESS("Starting XML-RPC server on http://localhost:8001..."))
        server.serve_forever()