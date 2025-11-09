from app.graph import Graph
from typing import Dict, List, Any, Set
import random

def find_nearest_idle_driver(source, drivers, graph: Graph):
    best, best_dist = None, float('inf')
    for d in [x for x in drivers if x['status'] == 'idle']:
        dist = graph.dijkstra(d['location'], source)['distance']
        if dist < best_dist:
            best, best_dist = d, dist
    return {'best_driver': best, 'min_pickup_dist': best_dist}

def find_best_pool_option(driver, request, graph: Graph):
    all_passengers = driver['passengers'] + [request]
    stops = [driver['location'], *[p['source'] for p in all_passengers], *[p['destination'] for p in all_passengers]]
    route = graph.get_multi_segment_route(stops)
    if route['distance'] == float('inf'):
        return None
    return {'distance': route['distance'], 'path': route['path'], 'stops': stops, 'passengers': all_passengers}
