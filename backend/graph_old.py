def get_graph():
    nodes = [
        # Zone A - Safe Entry (population: people at each node, capacity: max throughput)
        {"id": 0, "x": 100, "y": 50,  "zone": "A", "hazard": False, "population": 15, "capacity": 50, "label": "A0-Entry"},
        {"id": 1, "x": 60,  "y": 100, "zone": "A", "hazard": False, "population": 8,  "capacity": 30, "label": "A1"},
        {"id": 2, "x": 140, "y": 100, "zone": "A", "hazard": False, "population": 12, "capacity": 35, "label": "A2"},
        {"id": 3, "x": 100, "y": 150, "zone": "A", "hazard": False, "population": 10, "capacity": 40, "label": "A3"},
        {"id": 4, "x": 160, "y": 150, "zone": "A", "hazard": False, "population": 7,  "capacity": 25, "label": "A4"},
        {"id": 5, "x": 120, "y": 200, "zone": "A", "hazard": False, "population": 9,  "capacity": 30, "label": "A5"},

        # Zone B - Danger Zone (high population, high risk, limited capacity)
        {"id": 6,  "x": 120, "y": 260, "zone": "B", "hazard": False, "population": 25, "capacity": 20, "label": "B6"},
        {"id": 7,  "x": 80,  "y": 310, "zone": "B", "hazard": False, "population": 18, "capacity": 15, "label": "B7"},
        {"id": 8,  "x": 160, "y": 310, "zone": "B", "hazard": False, "population": 20, "capacity": 18, "label": "B8"},
        {"id": 9,  "x": 120, "y": 360, "zone": "B", "hazard": False, "population": 22, "capacity": 16, "label": "B9"},
        {"id": 10, "x": 60,  "y": 360, "zone": "B", "hazard": False, "population": 16, "capacity": 12, "label": "B10"},
        {"id": 11, "x": 180, "y": 360, "zone": "B", "hazard": False, "population": 19, "capacity": 14, "label": "B11"},
        {"id": 12, "x": 120, "y": 410, "zone": "B", "hazard": False, "population": 23, "capacity": 17, "label": "B12"},
        {"id": 13, "x": 120, "y": 460, "zone": "B", "hazard": False, "population": 21, "capacity": 15, "label": "B13"},

        # Zone C - Safe Corridor
        {"id": 14, "x": 70,  "y": 520, "zone": "C", "hazard": False, "population": 11, "capacity": 40, "label": "C14"},
        {"id": 15, "x": 170, "y": 520, "zone": "C", "hazard": False, "population": 13, "capacity": 42, "label": "C15"},
        {"id": 16, "x": 50,  "y": 580, "zone": "C", "hazard": False, "population": 9,  "capacity": 35, "label": "C16"},
        {"id": 17, "x": 100, "y": 580, "zone": "C", "hazard": False, "population": 10, "capacity": 38, "label": "C17"},
        {"id": 18, "x": 190, "y": 580, "zone": "C", "hazard": False, "population": 8,  "capacity": 36, "label": "C18"},
        {"id": 19, "x": 120, "y": 640, "zone": "C", "hazard": False, "population": 12, "capacity": 45, "label": "C19"},
        {"id": 20, "x": 80,  "y": 700, "zone": "C", "hazard": False, "population": 7,  "capacity": 50, "label": "C20"},
        {"id": 21, "x": 160, "y": 700, "zone": "C", "hazard": False, "population": 6,  "capacity": 50, "label": "C21"},

        # Exit Zone
        {"id": 22, "x": 120, "y": 760, "zone": "EXIT", "hazard": False, "population": 0, "capacity": 100, "label": "Exit-22"},
        {"id": 23, "x": 120, "y": 820, "zone": "EXIT", "hazard": False, "population": 0, "capacity": 100, "label": "Exit-23"},
    ]

    edges = [
        # Zone A (bidirectional)
        {"from": 0, "to": 1, "cost": 2, "risk": 1.0, "capacity": 40, "hazard": False, "blocked": False},
        {"from": 1, "to": 0, "cost": 2, "risk": 1.0, "capacity": 40, "hazard": False, "blocked": False},
        {"from": 0, "to": 2, "cost": 1, "risk": 1.0, "capacity": 45, "hazard": False, "blocked": False},
        {"from": 2, "to": 0, "cost": 1, "risk": 1.0, "capacity": 45, "hazard": False, "blocked": False},
        {"from": 1, "to": 3, "cost": 2, "risk": 1.2, "capacity": 35, "hazard": False, "blocked": False},
        {"from": 3, "to": 1, "cost": 2, "risk": 1.2, "capacity": 35, "hazard": False, "blocked": False},
        {"from": 2, "to": 3, "cost": 2, "risk": 1.2, "capacity": 35, "hazard": False, "blocked": False},
        {"from": 3, "to": 2, "cost": 2, "risk": 1.2, "capacity": 35, "hazard": False, "blocked": False},
        {"from": 2, "to": 4, "cost": 3, "risk": 1.4, "capacity": 30, "hazard": False, "blocked": False},
        {"from": 4, "to": 2, "cost": 3, "risk": 1.4, "capacity": 30, "hazard": False, "blocked": False},
        {"from": 3, "to": 5, "cost": 2, "risk": 1.2, "capacity": 35, "hazard": False, "blocked": False},
        {"from": 5, "to": 3, "cost": 2, "risk": 1.2, "capacity": 35, "hazard": False, "blocked": False},
        {"from": 4, "to": 5, "cost": 2, "risk": 1.2, "capacity": 30, "hazard": False, "blocked": False},
        {"from": 5, "to": 4, "cost": 2, "risk": 1.2, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 5, "to": 6, "cost": 3, "risk": 1.6, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 6, "to": 5, "cost": 3, "risk": 1.6, "capacity": 25, "hazard": False, "blocked": False},

        # Zone B (dangerous, bidirectional)
        {"from": 6, "to": 7, "cost": 7, "risk": 4.5, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 7, "to": 6, "cost": 7, "risk": 4.5, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 6, "to": 8, "cost": 8, "risk": 4.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 8, "to": 6, "cost": 8, "risk": 4.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 7, "to": 9, "cost": 6, "risk": 4.0, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 9, "to": 7, "cost": 6, "risk": 4.0, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 8, "to": 9, "cost": 6, "risk": 4.0, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 9, "to": 8, "cost": 6, "risk": 4.0, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 7, "to": 10, "cost": 8, "risk": 4.6, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 10, "to": 7, "cost": 8, "risk": 4.6, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 8, "to": 11, "cost": 8, "risk": 4.6, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 11, "to": 8, "cost": 8, "risk": 4.6, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 9, "to": 12, "cost": 7, "risk": 4.4, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 12, "to": 9, "cost": 7, "risk": 4.4, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 10, "to": 12, "cost": 9, "risk": 4.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 12, "to": 10, "cost": 9, "risk": 4.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 11, "to": 12, "cost": 9, "risk": 4.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 12, "to": 11, "cost": 9, "risk": 4.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 12, "to": 13, "cost": 7, "risk": 4.2, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 13, "to": 12, "cost": 7, "risk": 4.2, "capacity": 25, "hazard": False, "blocked": False},

        # Zone C (bidirectional)
        {"from": 13, "to": 14, "cost": 4, "risk": 2.0, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 14, "to": 13, "cost": 4, "risk": 2.0, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 13, "to": 15, "cost": 4, "risk": 2.0, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 15, "to": 13, "cost": 4, "risk": 2.0, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 14, "to": 16, "cost": 3, "risk": 1.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 16, "to": 14, "cost": 3, "risk": 1.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 14, "to": 17, "cost": 3, "risk": 1.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 17, "to": 14, "cost": 3, "risk": 1.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 15, "to": 18, "cost": 3, "risk": 1.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 18, "to": 15, "cost": 3, "risk": 1.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 16, "to": 19, "cost": 4, "risk": 1.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 19, "to": 16, "cost": 4, "risk": 1.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 17, "to": 19, "cost": 4, "risk": 1.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 19, "to": 17, "cost": 4, "risk": 1.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 18, "to": 19, "cost": 4, "risk": 1.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 19, "to": 18, "cost": 4, "risk": 1.9, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 19, "to": 20, "cost": 2, "risk": 1.2, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 20, "to": 19, "cost": 2, "risk": 1.2, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 19, "to": 21, "cost": 2, "risk": 1.2, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 21, "to": 19, "cost": 2, "risk": 1.2, "capacity": 25, "hazard": False, "blocked": False},

        # Exit (bidirectional)
        {"from": 20, "to": 22, "cost": 1, "risk": 0.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 22, "to": 20, "cost": 1, "risk": 0.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 21, "to": 22, "cost": 1, "risk": 0.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 22, "to": 21, "cost": 1, "risk": 0.8, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 22, "to": 23, "cost": 1, "risk": 0.5, "capacity": 25, "hazard": False, "blocked": False},
        {"from": 23, "to": 22, "cost": 1, "risk": 0.5, "capacity": 25, "hazard": False, "blocked": False},
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "start": 0,
        "end": 23
    }


def get_zone_metadata():
    """Return zone-specific constraints and properties"""
    return {
        "A": {
            "name": "Safe Entry Zone",
            "color": "#4ade80",  # green
            "time_window": {"min": 0, "max": 10},  # minutes
            "description": "Initial safe zone - must evacuate within 10 minutes"
        },
        "B": {
            "name": "Danger Zone",
            "color": "#f87171",  # red
            "time_window": {"min": 5, "max": 15},  # minutes
            "description": "High-risk area - limited time window"
        },
        "C": {
            "name": "Safe Corridor",
            "color": "#60a5fa",  # blue
            "time_window": {"min": 10, "max": 20},  # minutes
            "description": "Transit zone towards exit"
        },
        "EXIT": {
            "name": "Exit Zone",
            "color": "#a78bfa",  # purple
            "time_window": {"min": 0, "max": 30},  # minutes
            "description": "Final evacuation point"
        }
    }


def get_constraint_config():
    """Hard constraints for evacuation problem"""
    return {
        "vehicle_capacity": 50,  # people per rescue vehicle
        "num_vehicles": 3,  # available rescue teams
        "total_population": 301,  # sum of all node populations
        "time_limit": 30,  # minutes to complete evacuation
        "constraint_penalty": 1000,  # penalty weight for constraint violations
    }
