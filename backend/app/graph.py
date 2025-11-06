import heapq
from typing import Dict, Any, List, Tuple

NodeId = str
Path = List[NodeId]

class Graph:
    def __init__(self):
        self.nodes: Dict[NodeId, Dict[str, Any]] = {}
        self.adjacency_list: Dict[NodeId, List[Dict[str, Any]]] = {}

    def add_node(self, id: NodeId, lat: float, lng: float, name: str = None):
        self.nodes[id] = {'id': id, 'lat': lat, 'lng': lng, 'name': name or id}
        if id not in self.adjacency_list:
            self.adjacency_list[id] = []

    def add_edge(self, u: NodeId, v: NodeId, weight: float):
        if u not in self.adjacency_list: self.adjacency_list[u] = []
        if v not in self.adjacency_list: self.adjacency_list[v] = []
        self.adjacency_list[u].append({'node': v, 'weight': weight})
        self.adjacency_list[v].append({'node': u, 'weight': weight})

    def get_node(self, id: NodeId):
        return self.nodes.get(id)

    def dijkstra(self, source: NodeId, target: NodeId):
        distances = {node: float('inf') for node in self.nodes}
        previous = {node: None for node in self.nodes}
        pq = [(0.0, source)]
        distances[source] = 0.0
        while pq:
            dist, node = heapq.heappop(pq)
            if dist > distances[node]:
                continue
            if node == target:
                break
            for n in self.adjacency_list.get(node, []):
                new_dist = dist + n['weight']
                if new_dist < distances[n['node']]:
                    distances[n['node']] = new_dist
                    previous[n['node']] = node
                    heapq.heappush(pq, (new_dist, n['node']))
        path = []
        current = target
        while current is not None:
            path.insert(0, current)
            current = previous[current]
        return {'distance': distances[target], 'path': path}

    def get_multi_segment_route(self, stops: List[NodeId]):
        total = 0.0
        path: Path = []
        if len(stops) < 2:
            return {'distance': 0.0, 'path': []}
        for i in range(len(stops) - 1):
            seg = self.dijkstra(stops[i], stops[i + 1])
            total += seg['distance']
            path.extend(seg['path'] if i == 0 else seg['path'][1:])
        return {'distance': total, 'path': path}
