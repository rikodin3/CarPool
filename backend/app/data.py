import random

SAMPLE_GRAPH = {
    "Library": {"School": 3, "Park": 2},
    "School": {"Library": 3, "Grocery Store": 4, "Hospital": 6},
    "Grocery Store": {"School": 4, "Fire Station": 5},
    "Park": {"Library": 2, "Community Center": 3, "Hospital": 5},
    "Hospital": {"School": 6, "Park": 5, "Police Station": 4},
    "Community Center": {"Park": 3, "Fire Station": 2},
    "Fire Station": {"Community Center": 2, "Grocery Store": 5, "Police Station": 3},
    "Police Station": {"Hospital": 4, "Fire Station": 3, "Town Hall": 4},
    "Town Hall": {"Police Station": 4, "Cafe": 2},
    "Cafe": {"Town Hall": 2}
}

LOCATIONS = list(SAMPLE_GRAPH.keys())

def generate_initial_drivers(num_drivers = 3):
    drivers = []
    for i in range(1, num_drivers):
        start_location = random.choice(LOCATIONS)
        drivers.append({
            "id": f"Driver {i}",
            "location": start_location
        })
    return drivers

INITIAL_DRIVERS = generate_initial_drivers()

SAMPLE_REQUESTS = [
    {"userId": "U1", "source": "Library", "destination": "Cafe"},
    {"userId": "U2", "source": "Community Center", "destination": "Hospital"},
    {"userId": "U3", "source": "Grocery Store", "destination": "Park"}
]   