import random
from app.data import SAMPLE_GRAPH, initialize_drivers
from app.graph import Graph
from app.carpooling import find_nearest_idle_driver, find_best_pool_option

class CarpoolSimulator:
    def __init__(self):
        self.graph = Graph()
        for node in SAMPLE_GRAPH['nodes']:
            self.graph.add_node(node['id'], node['lat'], node['lng'], node['name'])
        for edge in SAMPLE_GRAPH['edges']:
            self.graph.add_edge(edge['u'], edge['v'], edge['weight'])
        self.drivers = initialize_drivers(3, SAMPLE_GRAPH['nodes'])
        self.requests = []
        self.history = []

    def get_full_status(self):
        return {'drivers': self.drivers, 'requests': self.requests, 'history': self.history}

    def submit_request(self, user_id, source, dest):
        new_req = {'id': f'R-{random.randint(1000,9999)}', 'userId': user_id, 'source': source, 'destination': dest}
        idle = find_nearest_idle_driver(source, self.drivers, self.graph)
        best_driver, dist = idle['best_driver'], idle['min_pickup_dist']
        if not best_driver:
            self.requests.append(new_req)
            return {'success': False, 'message': 'No available drivers.'}

        route = self.graph.get_multi_segment_route([best_driver['location'], source, dest])
        best_driver.update({'status': 'en-route', 'passengers': [new_req], 'current_route_stops': [source, dest]})
        self.history.append({'driver': best_driver['id'], 'request': new_req, 'distance': route['distance']})
        return {'success': True, 'message': f"Assigned {best_driver['id']} to {user_id}!", 'route': route}

simulator = CarpoolSimulator()
