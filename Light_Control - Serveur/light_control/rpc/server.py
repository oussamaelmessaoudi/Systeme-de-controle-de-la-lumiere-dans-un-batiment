from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import threading
import os
import django
import sys 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'light_control.settings')
django.setup()

from core.models import Zone, ActivityLog

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class XMLRPCServer:
    def __init__(self, host='localhost', port=8001):
        self.server = SimpleXMLRPCServer((host, port),
                                         requestHandler=RequestHandler,
                                         allow_none=True)
        self.server.register_function(self.set_light_state)
        self.server.register_function(self.get_light_state)
        self.server_thread = None
        self.running = False

    def set_light_state(self, zone_id, state):
        """Change l'état d'une lumière pour une zone donnée"""
        try:
            zone = Zone.objects.get(id=zone_id)
            # Ici, simule le changement d'état
            # Dans un système réel, on communiquerait avec le hardware
            zone.current_state = bool(state)
            zone.save()
            
            # Enregistrer l'action
            ActivityLog.record_activity(
                action='ON' if state else 'OFF',
                source='SYSTEM',
                zone=zone,
                details=f"Light state changed to {'ON' if state else 'OFF'} via RPC"
            )
            
            return {
                'success': True, 
                'zone_id': zone_id, 
                'state': zone.current_state
            }
        except Zone.DoesNotExist:
            return {'success': False, 'error': f"Zone {zone_id} not found"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_light_state(self, zone_id):
        """Récupère l'état actuel d'une lumière"""
        try:
            zone = Zone.objects.get(id=zone_id)
            return {
                'success': True, 
                'zone_id': zone_id, 
                'state': zone.current_state
            }
        except Zone.DoesNotExist:
            return {'success': False, 'error': f"Zone {zone_id} not found"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def start_server(self):
        """Démarre le serveur RPC dans un thread séparé"""
        if self.running:
            return
            
        self.running = True
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"XML-RPC Server running on http://localhost:8001/RPC2")

    def stop_server(self):
        """Arrête le serveur RPC"""
        if not self.running:
            return
            
        self.server.shutdown()
        self.running = False
        print("XML-RPC Server stopped")

# Pour exécuter le serveur directement
if __name__ == "__main__":
    server = XMLRPCServer()
    try:
        server.start_server()
        print("Press Ctrl+C to stop")
        while True:
            pass
    except KeyboardInterrupt:
        server.stop_server()