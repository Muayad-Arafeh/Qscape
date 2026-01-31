def get_graph():
    nodes = [
        # Zone A
        {"id": 0, "x": 100, "y": 50,  "zone": "A"},
        {"id": 1, "x": 60,  "y": 100, "zone": "A"},
        {"id": 2, "x": 140, "y": 100, "zone": "A"},
        {"id": 3, "x": 100, "y": 150, "zone": "A"},
        {"id": 4, "x": 160, "y": 150, "zone": "A"},
        {"id": 5, "x": 120, "y": 200, "zone": "A"},

        # Zone B (high risk)
        {"id": 6,  "x": 120, "y": 260, "zone": "B"},
        {"id": 7,  "x": 80,  "y": 310, "zone": "B"},
        {"id": 8,  "x": 160, "y": 310, "zone": "B"},
        {"id": 9,  "x": 120, "y": 360, "zone": "B"},
        {"id": 10, "x": 60,  "y": 360, "zone": "B"},
        {"id": 11, "x": 180, "y": 360, "zone": "B"},
        {"id": 12, "x": 120, "y": 410, "zone": "B"},
        {"id": 13, "x": 120, "y": 460, "zone": "B"},

        # Zone C
        {"id": 14, "x": 70,  "y": 520, "zone": "C"},
        {"id": 15, "x": 170, "y": 520, "zone": "C"},
        {"id": 16, "x": 50,  "y": 580, "zone": "C"},
        {"id": 17, "x": 100, "y": 580, "zone": "C"},
        {"id": 18, "x": 190, "y": 580, "zone": "C"},
        {"id": 19, "x": 120, "y": 640, "zone": "C"},
        {"id": 20, "x": 80,  "y": 700, "zone": "C"},
        {"id": 21, "x": 160, "y": 700, "zone": "C"},

        # Exit
        {"id": 22, "x": 120, "y": 760, "zone": "EXIT"},
        {"id": 23, "x": 120, "y": 820, "zone": "EXIT"},
    ]

    edges = [
        # Zone A
        {"from": 0, "to": 1, "cost": 2},
        {"from": 0, "to": 2, "cost": 1},
        {"from": 1, "to": 3, "cost": 2},
        {"from": 2, "to": 3, "cost": 2},
        {"from": 2, "to": 4, "cost": 3},
        {"from": 3, "to": 5, "cost": 2},
        {"from": 4, "to": 5, "cost": 2},
        {"from": 5, "to": 6, "cost": 3},

        # Zone B (dangerous)
        {"from": 6, "to": 7, "cost": 7},
        {"from": 6, "to": 8, "cost": 8},
        {"from": 7, "to": 9, "cost": 6},
        {"from": 8, "to": 9, "cost": 6},
        {"from": 7, "to": 10, "cost": 8},
        {"from": 8, "to": 11, "cost": 8},
        {"from": 9, "to": 12, "cost": 7},
        {"from": 10, "to": 12, "cost": 9},
        {"from": 11, "to": 12, "cost": 9},
        {"from": 12, "to": 13, "cost": 7},

        # Zone C
        {"from": 13, "to": 14, "cost": 4},
        {"from": 13, "to": 15, "cost": 4},
        {"from": 14, "to": 16, "cost": 3},
        {"from": 14, "to": 17, "cost": 3},
        {"from": 15, "to": 18, "cost": 3},
        {"from": 16, "to": 19, "cost": 4},
        {"from": 17, "to": 19, "cost": 4},
        {"from": 18, "to": 19, "cost": 4},
        {"from": 19, "to": 20, "cost": 2},
        {"from": 19, "to": 21, "cost": 2},

        # Exit
        {"from": 20, "to": 22, "cost": 1},
        {"from": 21, "to": 22, "cost": 1},
        {"from": 22, "to": 23, "cost": 1},
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "start": 0,
        "end": 23
    }
