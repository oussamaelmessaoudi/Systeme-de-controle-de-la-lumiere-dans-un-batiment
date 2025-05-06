import xmlrpc.client

class RPCClient:
    def __init__(self, server_url='http://localhost:8001/RPC2'):
        self.server = xmlrpc.client.ServerProxy(server_url)
    
    def set_light_state(self, zone_id, state):
        """Appelle la méthode distante pour changer l'état d'une lumière"""
        try:
            return self.server.set_light_state(zone_id, state)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_light_state(self, zone_id):
        """Appelle la méthode distante pour obtenir l'état d'une lumière"""
        try:
            return self.server.get_light_state(zone_id)
        except Exception as e:
            return {'success': False, 'error': str(e)}