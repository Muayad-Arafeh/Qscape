def get_graph():
    nodes = [
        # Zone A
        {"id": 0, "x": 100, "y": 50,  "zone": "A", "hazard": False},
        {"id": 1, "x": 60,  "y": 100, "zone": "A", "hazard": False},
        {"id": 2, "x": 140, "y": 100, "zone": "A", "hazard": False},
        {"id": 3, "x": 100, "y": 150, "zone": "A", "hazard": False},
        {"id": 4, "x": 160, "y": 150, "zone": "A", "hazard": False},
        {"id": 5, "x": 120, "y": 200, "zone": "A", "hazard": False},

        # Zone B (high risk)
        {"id": 6,  "x": 120, "y": 260, "zone": "B", "hazard": False},
        {"id": 7,  "x": 80,  "y": 310, "zone": "B", "hazard": False},
        {"id": 8,  "x": 160, "y": 310, "zone": "B", "hazard": False},
        {"id": 9,  "x": 120, "y": 360, "zone": "B", "hazard": False},
        {"id": 10, "x": 60,  "y": 360, "zone": "B", "hazard": False},
        {"id": 11, "x": 180, "y": 360, "zone": "B", "hazard": False},
        {"id": 12, "x": 120, "y": 410, "zone": "B", "hazard": False},
        {"id": 13, "x": 120, "y": 460, "zone": "B", "hazard": False},

        # Zone C
        {"id": 14, "x": 70,  "y": 520, "zone": "C", "hazard": False},
        {"id": 15, "x": 170, "y": 520, "zone": "C", "hazard": False},
        {"id": 16, "x": 50,  "y": 580, "zone": "C", "hazard": False},
        {"id": 17, "x": 100, "y": 580, "zone": "C", "hazard": False},
        {"id": 18, "x": 190, "y": 580, "zone": "C", "hazard": False},
        {"id": 19, "x": 120, "y": 640, "zone": "C", "hazard": False},
        {"id": 20, "x": 80,  "y": 700, "zone": "C", "hazard": False},
        {"id": 21, "x": 160, "y": 700, "zone": "C", "hazard": False},

        # Exit
        {"id": 22, "x": 120, "y": 760, "zone": "EXIT", "hazard": False},
        {"id": 23, "x": 120, "y": 820, "zone": "EXIT", "hazard": False},
    ]

    edges = [
        # Zone A
        {"from": 0, "to": 1, "cost": 2, "risk": 1.0, "hazard": False, "blocked": False},
        {"from": 0, "to": 2, "cost": 1, "risk": 1.0, "hazard": False, "blocked": False},
        {"from": 1, "to": 3, "cost": 2, "risk": 1.2, "hazard": False, "blocked": False},
        {"from": 2, "to": 3, "cost": 2, "risk": 1.2, "hazard": False, "blocked": False},
        {"from": 2, "to": 4, "cost": 3, "risk": 1.4, "hazard": False, "blocked": False},
        {"from": 3, "to": 5, "cost": 2, "risk": 1.2, "hazard": False, "blocked": False},
        {"from": 4, "to": 5, "cost": 2, "risk": 1.2, "hazard": False, "blocked": False},
        {"from": 5, "to": 6, "cost": 3, "risk": 1.6, "hazard": False, "blocked": False},

        # Zone B (dangerous)
        {"from": 6, "to": 7, "cost": 7, "risk": 4.5, "hazard": False, "blocked": False},
        {"from": 6, "to": 8, "cost": 8, "risk": 4.8, "hazard": False, "blocked": False},
        {"from": 7, "to": 9, "cost": 6, "risk": 4.0, "hazard": False, "blocked": False},
        {"from": 8, "to": 9, "cost": 6, "risk": 4.0, "hazard": False, "blocked": False},
        {"from": 7, "to": 10, "cost": 8, "risk": 4.6, "hazard": False, "blocked": False},
        {"from": 8, "to": 11, "cost": 8, "risk": 4.6, "hazard": False, "blocked": False},
        {"from": 9, "to": 12, "cost": 7, "risk": 4.4, "hazard": False, "blocked": False},
        {"from": 10, "to": 12, "cost": 9, "risk": 4.9, "hazard": False, "blocked": False},
        {"from": 11, "to": 12, "cost": 9, "risk": 4.9, "hazard": False, "blocked": False},
        {"from": 12, "to": 13, "cost": 7, "risk": 4.2, "hazard": False, "blocked": False},

        # Zone C
        {"from": 13, "to": 14, "cost": 4, "risk": 2.0, "hazard": False, "blocked": False},
        {"from": 13, "to": 15, "cost": 4, "risk": 2.0, "hazard": False, "blocked": False},
        {"from": 14, "to": 16, "cost": 3, "risk": 1.8, "hazard": False, "blocked": False},
        {"from": 14, "to": 17, "cost": 3, "risk": 1.8, "hazard": False, "blocked": False},
        {"from": 15, "to": 18, "cost": 3, "risk": 1.8, "hazard": False, "blocked": False},
        {"from": 16, "to": 19, "cost": 4, "risk": 1.9, "hazard": False, "blocked": False},
        {"from": 17, "to": 19, "cost": 4, "risk": 1.9, "hazard": False, "blocked": False},
        {"from": 18, "to": 19, "cost": 4, "risk": 1.9, "hazard": False, "blocked": False},
        {"from": 19, "to": 20, "cost": 2, "risk": 1.2, "hazard": False, "blocked": False},
        {"from": 19, "to": 21, "cost": 2, "risk": 1.2, "hazard": False, "blocked": False},

        # Exit
        {"from": 20, "to": 22, "cost": 1, "risk": 0.8, "hazard": False, "blocked": False},
        {"from": 21, "to": 22, "cost": 1, "risk": 0.8, "hazard": False, "blocked": False},
        {"from": 22, "to": 23, "cost": 1, "risk": 0.5, "hazard": False, "blocked": False},
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "start": 0,
        "end": 23
    }
