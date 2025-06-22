import xmlrpc.client


class LightController:
    def __init__(self, server_url="http://localhost:8001"):
        self.server = xmlrpc.client.ServerProxy(server_url)

    def turn_on(self, zone_id):
        """Allume les lumières d'une zone."""
        try:
            return self.server.turn_on(zone_id)
        except Exception as e:
            raise Exception(f"Failed to turn on lights for zone {zone_id}: {str(e)}")

    def turn_off(self, zone_id):
        """Éteint les lumières d'une zone."""
        try:
            return self.server.turn_off(zone_id)
        except Exception as e:
            raise Exception(f"Failed to turn off lights for zone {zone_id}: {str(e)}")

    def get_state(self, zone_id):
        """Récupère l'état actuel d'une zone."""
        try:
            return self.server.get_state(zone_id)
        except Exception as e:
            raise Exception(f"Failed to get state for zone {zone_id}: {str(e)}")
        
    def toggle_lamp(self, lamp_id):
        """Toggles a single lamp."""
        try:
            return self.server.toggle_lamp(lamp_id)
        except Exception as e:
            raise Exception(f"Failed to toggle lamp {lamp_id}: {str(e)}")