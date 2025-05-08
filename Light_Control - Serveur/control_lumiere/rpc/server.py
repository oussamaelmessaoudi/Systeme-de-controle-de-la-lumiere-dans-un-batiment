from xmlrpc.server import SimpleXMLRPCServer


class LightControlServer:
    def turn_on(self, zone_id):
        print(f"Turning on lights for zone {zone_id}")
        return True

    def turn_off(self, zone_id):
        print(f"Turning off lights for zone {zone_id}")
        return True

    def get_state(self, zone_id):
        print(f"Getting state for zone {zone_id}")
        return False  # Exemple


def run_server():
    server = SimpleXMLRPCServer(("localhost", 8001))
    server.register_instance(LightControlServer())
    print("Starting RPC server on port 8001...")
    server.serve_forever()


if __name__ == "__main__":
    run_server()