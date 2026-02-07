def get_graph():
    # SIMPLIFIED GRAPH - Node by node, easy to modify
    # No clustering, no complex functions!
    
    nodes = [
        # START/END nodes
        {"id": 0, "x": 100, "y": 100, "zone": "START", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 15, "capacity": 50, "label": "START"},
        {"id": 1, "x": 600, "y": 1200, "zone": "END", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 90, "label": "END"},
        
        # Residential Zone 1 (ids 2-7)
        {"id": 2, "x": 100, "y": 200, "zone": "RES1", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 10, "capacity": 40, "label": "R1-2"},
        {"id": 3, "x": 200, "y": 200, "zone": "RES1", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 12, "capacity": 45, "label": "R1-3"},
        {"id": 4, "x": 100, "y": 300, "zone": "RES1", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 8, "capacity": 35, "label": "R1-4"},
        {"id": 5, "x": 200, "y": 300, "zone": "RES1", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 11, "capacity": 42, "label": "R1-5"},
        {"id": 6, "x": 150, "y": 400, "zone": "RES1", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 9, "capacity": 38, "label": "R1-6"},
        {"id": 7, "x": 250, "y": 400, "zone": "RES1", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 10, "capacity": 40, "label": "R1-7"},
        
        # Residential Zone 2 (ids 8-13)
        {"id": 8, "x": 800, "y": 150, "zone": "RES2", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 10, "capacity": 40, "label": "R2-8"},
        {"id": 9, "x": 900, "y": 150, "zone": "RES2", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 12, "capacity": 45, "label": "R2-9"},
        {"id": 10, "x": 850, "y": 250, "zone": "RES2", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 8, "capacity": 35, "label": "R2-10"},
        {"id": 11, "x": 950, "y": 250, "zone": "RES2", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 11, "capacity": 42, "label": "R2-11"},
        {"id": 12, "x": 800, "y": 350, "zone": "RES2", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 9, "capacity": 38, "label": "R2-12"},
        {"id": 13, "x": 900, "y": 350, "zone": "RES2", "region_type": "Residential Zone", "hazard": False, "blocked": False, "population": 10, "capacity": 40, "label": "R2-13"},
        
        # Transition Zone (ids 14-23)
        {"id": 14, "x": 400, "y": 200, "zone": "TRANS1", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 6, "capacity": 30, "label": "T1-14"},
        {"id": 15, "x": 500, "y": 200, "zone": "TRANS1", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 7, "capacity": 32, "label": "T1-15"},
        {"id": 16, "x": 600, "y": 200, "zone": "TRANS1", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 5, "capacity": 28, "label": "T1-16"},
        {"id": 17, "x": 450, "y": 300, "zone": "TRANS1", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 6, "capacity": 30, "label": "T1-17"},
        {"id": 18, "x": 550, "y": 300, "zone": "TRANS1", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 8, "capacity": 35, "label": "T1-18"},
        {"id": 19, "x": 400, "y": 450, "zone": "TRANS2", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 6, "capacity": 30, "label": "T2-19"},
        {"id": 20, "x": 500, "y": 450, "zone": "TRANS2", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 7, "capacity": 32, "label": "T2-20"},
        {"id": 21, "x": 600, "y": 450, "zone": "TRANS2", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 6, "capacity": 30, "label": "T2-21"},
        {"id": 22, "x": 500, "y": 550, "zone": "TRANS2", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 8, "capacity": 35, "label": "T2-22"},
        {"id": 23, "x": 600, "y": 550, "zone": "TRANS2", "region_type": "Transition Zone", "hazard": False, "blocked": False, "population": 7, "capacity": 32, "label": "T2-23"},
        
        # High-Risk Zones (ids 24-34)
        {"id": 24, "x": 150, "y": 550, "zone": "RISK1", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 20, "capacity": 15, "label": "HR1-24"},
        {"id": 25, "x": 250, "y": 550, "zone": "RISK1", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 22, "capacity": 18, "label": "HR1-25"},
        {"id": 26, "x": 150, "y": 650, "zone": "RISK1", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 19, "capacity": 14, "label": "HR1-26"},
        {"id": 27, "x": 250, "y": 650, "zone": "RISK1", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 21, "capacity": 16, "label": "HR1-27"},
        {"id": 28, "x": 200, "y": 750, "zone": "RISK1", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 20, "capacity": 15, "label": "HR1-28"},
        {"id": 29, "x": 800, "y": 550, "zone": "RISK2", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 20, "capacity": 15, "label": "HR2-29"},
        {"id": 30, "x": 900, "y": 550, "zone": "RISK2", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 22, "capacity": 18, "label": "HR2-30"},
        {"id": 31, "x": 850, "y": 650, "zone": "RISK2", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 19, "capacity": 14, "label": "HR2-31"},
        {"id": 32, "x": 950, "y": 650, "zone": "RISK2", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 21, "capacity": 16, "label": "HR2-32"},
        {"id": 33, "x": 850, "y": 750, "zone": "RISK2", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 20, "capacity": 15, "label": "HR2-33"},
        {"id": 34, "x": 950, "y": 750, "zone": "RISK2", "region_type": "High-Risk Zone", "hazard": False, "blocked": False, "population": 18, "capacity": 12, "label": "HR2-34"},
        
        # Control Zones (ids 35-40)
        {"id": 35, "x": 350, "y": 900, "zone": "CTRL1", "region_type": "Conflict / Control Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 18, "label": "C1-35"},
        {"id": 36, "x": 450, "y": 900, "zone": "CTRL1", "region_type": "Conflict / Control Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 16, "label": "C1-36"},
        {"id": 37, "x": 400, "y": 1000, "zone": "CTRL1", "region_type": "Conflict / Control Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 20, "label": "C1-37"},
        {"id": 38, "x": 650, "y": 900, "zone": "CTRL2", "region_type": "Conflict / Control Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 18, "label": "C2-38"},
        {"id": 39, "x": 750, "y": 900, "zone": "CTRL2", "region_type": "Conflict / Control Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 16, "label": "C2-39"},
        {"id": 40, "x": 700, "y": 1000, "zone": "CTRL2", "region_type": "Conflict / Control Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 20, "label": "C2-40"},
        
        # Safe Zones (ids 41-50)
        {"id": 41, "x": 550, "y": 1100, "zone": "SAFE1", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 80, "label": "S1-41"},
        {"id": 42, "x": 650, "y": 1100, "zone": "SAFE1", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 85, "label": "S1-42"},
        {"id": 43, "x": 550, "y": 1200, "zone": "SAFE1", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 1, "capacity": 75, "label": "S1-43"},
        {"id": 44, "x": 650, "y": 1200, "zone": "SAFE1", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 2, "capacity": 90, "label": "S1-44"},
        {"id": 45, "x": 150, "y": 1100, "zone": "SAFE2", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 70, "label": "S2-45"},
        {"id": 46, "x": 250, "y": 1100, "zone": "SAFE2", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 1, "capacity": 75, "label": "S2-46"},
        {"id": 47, "x": 200, "y": 1200, "zone": "SAFE2", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 2, "capacity": 80, "label": "S2-47"},
        {"id": 48, "x": 850, "y": 1100, "zone": "SAFE3", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 0, "capacity": 75, "label": "S3-48"},
        {"id": 49, "x": 950, "y": 1100, "zone": "SAFE3", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 1, "capacity": 80, "label": "S3-49"},
        {"id": 50, "x": 900, "y": 1200, "zone": "SAFE3", "region_type": "Safe Zone", "hazard": False, "blocked": False, "population": 2, "capacity": 85, "label": "S3-50"},
    ]
    
    # Define edges as tuples: (from_id, to_id, cost, risk, capacity)
    edges_list = [
        # START to Residential
        (0, 2, 2.0, 1.0, 45),
        (0, 3, 2.0, 1.0, 45),
        
        # Residential 1 internal
        (2, 3, 2.0, 1.0, 40),
        (2, 4, 2.0, 1.0, 40),
        (3, 5, 2.0, 1.0, 40),
        (4, 5, 2.0, 1.0, 40),
        (4, 6, 2.0, 1.0, 40),
        (5, 7, 2.0, 1.0, 40),
        (6, 7, 2.0, 1.0, 40),
        
        # Residential 2 internal
        (8, 9, 2.0, 1.0, 40),
        (8, 10, 2.0, 1.0, 40),
        (9, 11, 2.0, 1.0, 40),
        (10, 11, 2.0, 1.0, 40),
        (10, 12, 2.0, 1.0, 40),
        (11, 13, 2.0, 1.0, 40),
        (12, 13, 2.0, 1.0, 40),
        
        # Transition 1 internal
        (14, 15, 3.0, 1.5, 35),
        (15, 16, 3.0, 1.5, 35),
        (14, 17, 3.0, 1.5, 35),
        (15, 17, 3.0, 1.5, 35),
        (15, 18, 3.0, 1.5, 35),
        (16, 18, 3.0, 1.5, 35),
        (17, 18, 3.0, 1.5, 35),
        
        # Transition 2 internal
        (19, 20, 3.0, 1.5, 35),
        (20, 21, 3.0, 1.5, 35),
        (19, 22, 3.0, 1.5, 35),
        (20, 22, 3.0, 1.5, 35),
        (21, 23, 3.0, 1.5, 35),
        (22, 23, 3.0, 1.5, 35),
        
        # Residential to Transition
        (5, 14, 3.0, 1.4, 38),
        (7, 17, 3.0, 1.4, 38),
        (8, 16, 3.0, 1.4, 38),
        (12, 18, 3.0, 1.4, 38),
        (6, 19, 3.0, 1.4, 38),
        (13, 21, 3.0, 1.4, 38),
        
        # High-Risk 1 internal
        (24, 25, 7.0, 4.5, 22),
        (24, 26, 7.0, 4.5, 22),
        (25, 27, 7.0, 4.5, 22),
        (26, 27, 7.0, 4.5, 22),
        (26, 28, 7.0, 4.5, 22),
        (27, 28, 7.0, 4.5, 22),
        
        # High-Risk 2 internal
        (29, 30, 7.0, 4.5, 22),
        (29, 31, 7.0, 4.5, 22),
        (30, 32, 7.0, 4.5, 22),
        (31, 32, 7.0, 4.5, 22),
        (31, 33, 7.0, 4.5, 22),
        (32, 34, 7.0, 4.5, 22),
        (33, 34, 7.0, 4.5, 22),
        
        # Transition to High-Risk
        (17, 24, 5.0, 3.5, 28),
        (18, 25, 5.0, 3.5, 28),
        (18, 29, 5.0, 3.5, 28),
        (19, 26, 5.0, 3.5, 28),
        (22, 27, 5.0, 3.5, 28),
        (23, 32, 5.0, 3.5, 28),
        (21, 30, 5.0, 3.5, 28),
        
        # Control zones internal
        (35, 36, 6.0, 5.0, 18),
        (35, 37, 6.0, 5.0, 18),
        (36, 37, 6.0, 5.0, 18),
        (38, 39, 6.0, 5.0, 18),
        (38, 40, 6.0, 5.0, 18),
        (39, 40, 6.0, 5.0, 18),
        
        # High-Risk to Control
        (27, 36, 8.0, 5.2, 20),
        (33, 38, 8.0, 5.2, 20),
        
        # Safe Zone 1 internal
        (41, 42, 1.0, 0.8, 80),
        (41, 43, 1.0, 0.8, 80),
        (42, 44, 1.0, 0.8, 80),
        (43, 44, 1.0, 0.8, 80),
        
        # Safe Zone 2 internal
        (45, 46, 1.0, 0.8, 80),
        (45, 47, 1.0, 0.8, 80),
        (46, 47, 1.0, 0.8, 80),
        
        # Safe Zone 3 internal
        (48, 49, 1.0, 0.8, 80),
        (48, 50, 1.0, 0.8, 80),
        (49, 50, 1.0, 0.8, 80),
        
        # High-Risk to Safe (bypassing Control zones - no overlap)
        (28, 45, 7.0, 3.5, 30),
        (27, 41, 7.0, 3.5, 30),
        (25, 46, 8.0, 3.7, 25),
        (33, 48, 7.0, 3.5, 28),
        (34, 49, 7.0, 3.5, 28),
        
        # Safe to END
        (43, 1, 1.0, 0.5, 85),
        (44, 1, 1.0, 0.5, 85),
    ]
    
    # Convert edge tuples to dict and make bidirectional
    edges = []
    
    for from_id, to_id, cost, risk, capacity in edges_list:
        # Forward direction
        edges.append({
            "from": from_id,
            "to": to_id,
            "cost": cost,
            "risk": risk,
            "capacity": capacity,
            "hazard": False,
            "blocked": False,
        })
        # Reverse direction
        edges.append({
            "from": to_id,
            "to": from_id,
            "cost": cost,
            "risk": risk,
            "capacity": capacity,
            "hazard": False,
            "blocked": False,
        })
    
    # Region profiles for attributes
    region_profiles = {
        "Residential Zone": {"risk_level": 2.0, "hazard_probability": 0.15, "congestion_score": 0.5},
        "Transition Zone": {"risk_level": 3.5, "hazard_probability": 0.35, "congestion_score": 0.7},
        "High-Risk Zone": {"risk_level": 8.0, "hazard_probability": 0.75, "congestion_score": 0.9},
        "Conflict / Control Zone": {"risk_level": 9.0, "hazard_probability": 0.85, "congestion_score": 0.95},
        "Safe Zone": {"risk_level": 0.5, "hazard_probability": 0.05, "congestion_score": 0.2},
    }
    
    # Apply region profiles to nodes
    for node in nodes:
        region_type = node.get("region_type", "Transition Zone")
        profile = region_profiles.get(region_type, region_profiles["Transition Zone"])
        node.setdefault("risk_level", profile["risk_level"])
        node.setdefault("hazard_probability", profile["hazard_probability"])
        node.setdefault("congestion_score", profile["congestion_score"])
    
    # Apply region-based multipliers to edges
    region_bonuses = {
        frozenset(["Residential Zone", "Residential Zone"]): 0.85,
        frozenset(["Transition Zone", "Transition Zone"]): 0.9,
        frozenset(["Safe Zone", "Safe Zone"]): 0.8,
    }
    region_penalties = {
        frozenset(["Residential Zone", "High-Risk Zone"]): 1.6,
        frozenset(["Transition Zone", "High-Risk Zone"]): 1.3,
        frozenset(["Safe Zone", "High-Risk Zone"]): 1.8,
        frozenset(["Residential Zone", "Conflict / Control Zone"]): 2.0,
    }
    
    node_regions = {node["id"]: node.get("region_type") for node in nodes}
    
    for edge in edges:
        if not edge.get("blocked"):
            region_a = node_regions.get(edge["from"])
            region_b = node_regions.get(edge["to"])
            if region_a and region_b:
                pair = frozenset([region_a, region_b])
                multiplier = region_bonuses.get(pair) or region_penalties.get(pair)
                if multiplier:
                    edge["cost"] = edge["cost"] * multiplier
                    edge["risk"] = edge["risk"] * multiplier
        
        edge.setdefault("base_distance", edge["cost"])
        edge.setdefault("dynamic_cost", edge["base_distance"] * edge["risk"])
    
    return {
        "nodes": nodes,
        "edges": edges,
        "start": 0,
        "end": 1
    }
