import random

SAMPLE_GRAPH = {
    'nodes': [
        {'id': 'A', 'name': 'Downtown', 'lat': 40.7128, 'lng': -74.0060},
        {'id': 'B', 'name': 'Midtown', 'lat': 40.7580, 'lng': -73.9855},
        {'id': 'C', 'name': 'Uptown', 'lat': 40.7829, 'lng': -73.9654},
        {'id': 'D', 'name': 'West Side', 'lat': 40.7489, 'lng': -74.0020},
        {'id': 'E', 'name': 'East Side', 'lat': 40.7489, 'lng': -73.9680},
        {'id': 'F', 'name': 'North End', 'lat': 40.8000, 'lng': -73.9500},
        {'id': 'G', 'name': 'South End', 'lat': 40.7000, 'lng': -74.0100},
        {'id': 'H', 'name': 'Harbor', 'lat': 40.7050, 'lng': -74.0200},
        {'id': 'I', 'name': 'Central Park', 'lat': 40.7711, 'lng': -73.9742},
        {'id': 'J', 'name': 'Brooklyn Edge', 'lat': 40.6900, 'lng': -73.9900},
        {'id': 'K', 'name': 'Queens Bridge', 'lat': 40.7570, 'lng': -73.9550},
    ],
    'edges': [
        {'u': 'A', 'v': 'B', 'weight': 5.2}, {'u': 'A', 'v': 'D', 'weight': 3.1},
        {'u': 'A', 'v': 'G', 'weight': 2.5}, {'u': 'A', 'v': 'J', 'weight': 1.8},
        {'u': 'B', 'v': 'C', 'weight': 3.8}, {'u': 'B', 'v': 'E', 'weight': 2.9},
        {'u': 'B', 'v': 'I', 'weight': 1.5}, {'u': 'C', 'v': 'F', 'weight': 2.2},
        {'u': 'D', 'v': 'E', 'weight': 4.5}, {'u': 'D', 'v': 'H', 'weight': 2.8},
        {'u': 'E', 'v': 'C', 'weight': 4.1}, {'u': 'E', 'v': 'K', 'weight': 3.3},
        {'u': 'F', 'v': 'I', 'weight': 1.9}, {'u': 'G', 'v': 'H', 'weight': 1.9},
        {'u': 'J', 'v': 'G', 'weight': 1.0}, {'u': 'K', 'v': 'B', 'weight': 2.5},
        {'u': 'H', 'v': 'D', 'weight': 2.8},
    ]
}

def initialize_drivers(count, nodes):
    drivers = []
    available = [n['id'] for n in nodes]
    for i in range(1, count + 1):
        node_id = random.choice(available)
        available.remove(node_id)
        drivers.append({
            'id': f'Driver-{i}', 'location': node_id, 'status': 'idle',
            'passengers': [], 'current_route_stops': [], 'final_destination': None
        })
    return drivers
