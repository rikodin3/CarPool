import heapq
from typing import Dict, Any, List, Tuple

NodeId = str
Path = List[NodeId]
Distance = float

class Graph:
    def __init__(self):
        # We are using adjacency list for graph representation for fast look up and memory effeciency
        self.nodes: Dict[NodeId, Dict[str, Any]]= {}
        self.adjacency_list: Dict[NodeId, List[Dict[str, Any]]] = {}

    def add_node(self, id:NodeId, lat: float, long: float, name: str = None):
        self.nodes[id] = {'id': id, 'lat': lat, 'long': long, 'name': name or id}
        if id not in self.adjacency_list:
            self.adjacency_list[id] = []

    def add_edge(self, u: NodeId, v:NodeId, weight:float):
        if u not in self.adjacency_list: self.adjacency_list[u] = []
        if v not in self.adjacency_list: self.adjacency_list[v] = []
        self.adjacency_list[u].append({'node': v, 'weight':weight})
        self.adjacency_list[v].append({'node': u, 'weight':weight})

    def get_node(self, id: NodeId) -> Dict[str, Any]:
        return self.nodes.get(id)
    
    def dijkstra(self, source: NodeId, target: NodeId):
        distances = {node: float('inf') for node in self.nodes}
        # for path reconstruction
        previous = {node: None for node in self.nodes}
        # we use priority queue to always process the closest element (implemented using a heap)
        pq = []

        distances[source] = 0.0
        heapq.heappush(pq, (0.0, source))
        nodes_explored = 0

        while pq:
            current_distance, current_node = heapq.heappop(pq)
            # skip if we already found a better path
            if current_distance > distances[current_node]:
                continue
            if current_node == target:
                break
            for neighbor_info in self.adjacency_list.get(current_node):
                neighbor = neighbor_info['node']
                weight = neighbor_info['weight']
                new_dist = current_distance + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))
        
        path = []
        current = target
        while current is not None:
            path.insert(0,current)
            current = previous[current]
        final_distance = distances.get(target, float('inf'))
        
        return {'distance':final_distance, 'path':path}
    
    def multi_segment_route(self, stops):
        """It basically chains various djikstra's call"""
        total_distance = 0.0
        full_path = []
        if len(stops) < 2:
            return {'distance':0.0, 'path':[]}
        
        for i in range(len(stops)-1):
            source, target = stops[i], stops[i+1]
            segment_result = self.dijkstra(source, target)
            total_distance += segment_result['distance']
            full_path.extend(segment_result['path'] if i==0 else segment_result['path'][1:])

        return {'distance': total_distance, 'path': full_path}
