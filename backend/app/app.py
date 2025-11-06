import heapq
import random
import itertools
from math import hypot
from typing import List, Dict, Any
from flask import Flask, jsonify, request
from flask_cors import CORS

# ---------------- GRAPH ----------------
SAMPLE_GRAPH = {
    'nodes': [
        {'id': 'A', 'name': 'Downtown', 'lat': 40.7128, 'lng': -74.0060},
        {'id': 'B', 'name': 'Midtown', 'lat': 40.7580, 'lng': -73.9855},
        {'id': 'C', 'name': 'Uptown', 'lat': 40.7829, 'lng': -73.9850},
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
        {'u': 'J', 'v': 'G', 'weight': 1.0}, {'u': 'K', 'v': 'B', 'weight': 2.5}
    ]
}

class Graph:
    def __init__(self):
        self.nodes = {}
        self.adj = {}

    def add_node(self, id, lat, lng, name=None):
        self.nodes[id] = {'id': id, 'lat': lat, 'lng': lng, 'name': name or id}
        self.adj.setdefault(id, [])

    def add_edge(self, u, v, w):
        self.adj.setdefault(u, []).append({'node': v, 'weight': w})
        self.adj.setdefault(v, []).append({'node': u, 'weight': w})

    def dijkstra(self, src, dst):
        dist = {n: float('inf') for n in self.nodes}
        prev = {n: None for n in self.nodes}
        dist[src] = 0
        pq = [(0, src)]
        while pq:
            d, n = heapq.heappop(pq)
            if n == dst: break
            for nb in self.adj[n]:
                nd = d + nb['weight']
                if nd < dist[nb['node']]:
                    dist[nb['node']] = nd
                    prev[nb['node']] = n
                    heapq.heappush(pq, (nd, nb['node']))
        path, cur = [], dst
        while cur:
            path.insert(0, cur)
            cur = prev[cur]
        return {'distance': dist[dst], 'path': path}

    def route(self, stops):
        total, path = 0, []
        if len(stops) < 2: return {'distance': 0, 'path': []}
        for i in range(len(stops) - 1):
            seg = self.dijkstra(stops[i], stops[i + 1])
            if seg['distance'] == float('inf'): return {'distance': float('inf'), 'path': []}
            total += seg['distance']
            path += seg['path'] if i == 0 else seg['path'][1:]
        return {'distance': total, 'path': path}

class CarpoolSimulator:
    MAX_DETOUR = 0.3
    CAPACITY = 3
    PROX_THRESHOLD = 0.015  # roughly ~1.5km equivalent

    def __init__(self):
        self.graph = Graph()
        for n in SAMPLE_GRAPH['nodes']:
            self.graph.add_node(n['id'], n['lat'], n['lng'], n['name'])
        for e in SAMPLE_GRAPH['edges']:
            self.graph.add_edge(e['u'], e['v'], e['weight'])
        self.drivers = self._init_drivers(3)
        self.requests, self.history = [], []

    def _init_drivers(self, n):
        nodes = [x['id'] for x in SAMPLE_GRAPH['nodes']]
        random.shuffle(nodes)
        return [{
            'id': f'Driver-{i+1}',
            'location': nodes[i],
            'status': 'idle',
            'passengers': [],
            'stops': []
        } for i in range(n)]

    def status(self):
        return {
            'nodes': list(self.graph.nodes.values()),
            'edges': SAMPLE_GRAPH['edges'],
            'drivers': self.drivers,
            'requests': self.requests,
            'rideHistory': self.history,
            'matches': []
        }

    def _geo(self, id): 
        n = self.graph.nodes[id]; 
        return (n['lat'], n['lng'])

    def _distance(self, a, b):
        la, loa = self._geo(a); lb, lob = self._geo(b)
        return hypot(la - lb, loa - lob)

    def _close(self, a, b):
        return self._distance(a, b) <= self.PROX_THRESHOLD
    
    def _find_best_pool(self, req):
        best = None
        for d in [x for x in self.drivers if x['status'] == 'en-route' and len(x['passengers']) < self.CAPACITY]:
            base_stops = [d['location']] + [p['source'] for p in d['passengers']] + [p['destination'] for p in d['passengers']]
            base_distance = self.graph.route(base_stops)['distance']
            passengers = d['passengers'] + [req]

            # Generate valid pickup/drop permutations
            pts = []
            for p in passengers:
                pts.append((p['source'], f"{p['userId']}_P"))
                pts.append((p['destination'], f"{p['userId']}_D"))

            for perm in itertools.permutations(pts):
                seen, seq, valid = set(), [], True
                for node, tag in perm:
                    uid, phase = tag.split('_')
                    if phase == 'P': seen.add(uid)
                    elif uid not in seen: valid = False; break
                    seq.append(node)
                if not valid: continue

                seq = [d['location']] + seq
                new_route = self.graph.route(seq)
                if new_route['distance'] == float('inf'): continue
                detour_ratio = (new_route['distance'] - base_distance) / max(base_distance, 0.1)
                if detour_ratio <= self.MAX_DETOUR:
                    if not best or new_route['distance'] < best['route']['distance']:
                        best = {'driver': d, 'route': new_route, 'stops': seq, 'detour': detour_ratio}
        return best

    def _find_idle_driver(self, req):
        best, best_dist = None, float('inf')
        for d in [x for x in self.drivers if x['status'] == 'idle']:
            dist = self.graph.dijkstra(d['location'], req['source'])['distance']
            if dist < best_dist:
                best, best_dist = d, dist
        if not best: return None
        route = self.graph.route([best['location'], req['source'], req['destination']])
        return {'driver': best, 'route': route}

    def _match_waiting_requests(self, req):
        """Try pooling with waiting riders having overlapping routes."""
        def route_overlap(r1, r2):
            s1, s2 = set(r1['path']), set(r2['path'])
            return len(s1 & s2) / max(1, min(len(s1), len(s2)))

        for other in self.requests:
            same_origin = self._close(req['source'], other['source'])
            if not same_origin:
                continue

            r1 = self.graph.route([req['source'], req['destination']])
            r2 = self.graph.route([other['source'], other['destination']])
            if r1['distance'] == float('inf') or r2['distance'] == float('inf'):
                continue

            overlap = route_overlap(r1, r2)
            if overlap >= 0.4:  # 40% overlap threshold
                # approximate detour cost by merging both destinations
                combo_route = self.graph.route([req['source'], other['destination'], req['destination']])
                detour = combo_route['distance'] - min(r1['distance'], r2['distance'])
                if detour / max(r1['distance'], r2['distance']) <= self.MAX_DETOUR:
                    idle = next((d for d in self.drivers if d['status'] == 'idle'), None)
                    if not idle: return None
                    idle.update({
                        'status': 'en-route',
                        'passengers': [req, other],
                        'stops': [req['source'], other['destination'], req['destination']]
                    })
                    self.requests.remove(other)
                    self.history.append({
                        'type': 'Pooled',
                        'driver': idle['id'],
                        'riders': [req['userId'], other['userId']],
                        'distance': combo_route['distance']
                    })
                    return {
                        'success': True,
                        'message': f"{req['userId']} pooled with {other['userId']} (shared route {overlap*100:.1f}%)",
                        'assigned_route': combo_route
                    }
        return None
    
    def submit(self, uid, src, dst):
        if not uid or not src or not dst:
            return {'success': False, 'message': 'Missing data'}
        req = {'id': f'R-{random.randint(1000,9999)}', 'userId': uid, 'source': src, 'destination': dst}

        # 1️⃣ Try to pool with existing drivers
        pool = self._find_best_pool(req)
        if pool:
            d = pool['driver']
            d['passengers'].append(req)
            d['stops'] = pool['stops']
            d['status'] = 'en-route'
            self.history.append({'type': 'Pooled', 'driver': d['id'], 'riders': [p['userId'] for p in d['passengers']], 'distance': pool['route']['distance']})
            return {'success': True, 'message': f"Pooled with {d['id']} (detour {pool['detour']*100:.1f}%)", 'assigned_route': pool['route']}

        # 2️⃣ Try pooling with waiting riders
        pair = self._match_waiting_requests(req)
        if pair:
            return pair

        # 3️⃣ Otherwise assign idle driver
        idle = self._find_idle_driver(req)
        if idle:
            d = idle['driver']
            d.update({'status': 'en-route', 'passengers': [req], 'stops': [src, dst]})
            self.history.append({'type': 'Assigned', 'driver': d['id'], 'riders': [uid], 'distance': idle['route']['distance']})
            return {'success': True, 'message': f"Assigned {d['id']} to {uid}", 'assigned_route': idle['route']}

        self.requests.append(req)
        return {'success': False, 'message': 'No drivers available; added to waiting list.'}

    def complete(self, did):
        d = next((x for x in self.drivers if x['id'] == did), None)
        if not d: return {'success': False, 'message': 'Driver not found'}
        d.update({'status': 'idle', 'passengers': [], 'stops': []})
        return {'success': True, 'message': f'{did} is now idle.'}

app = Flask(__name__)
CORS(app)
sim = CarpoolSimulator()

@app.route('/status')
def status(): return jsonify(sim.status())

@app.route('/submit-request', methods=['POST'])
def submit():
    d = request.json
    res = sim.submit(d.get('userId'), d.get('source'), d.get('destination'))
    return jsonify({**res, 'newState': sim.status()})

@app.route('/complete-ride', methods=['POST'])
def complete():
    d = request.json
    res = sim.complete(d.get('driverId'))
    return jsonify({**res, 'newState': sim.status()})

if __name__ == '__main__':
    print("✅ Smart Pooling Backend running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
