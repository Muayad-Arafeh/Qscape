"""
Constrained Optimization Module for Hard Evacuation Problems

This module handles capacity constraints, time windows, and multi-vehicle routing
to demonstrate quantum advantage on NP-hard problems.
"""

from typing import List, Dict, Tuple
import numpy as np


class ConstraintValidator:
    """Validates evacuation solutions against hard constraints"""
    
    def __init__(self, graph_data: Dict, config: Dict, zone_metadata: Dict):
        self.graph_data = graph_data
        self.config = config
        self.zone_metadata = zone_metadata
        
        # Build node lookup
        self.nodes = {n["id"]: n for n in graph_data["nodes"]}
        
    def validate_solution(self, path: List[int], execution_time: float) -> Tuple[bool, Dict]:
        """
        Validate if a path satisfies all constraints
        
        Returns:
            (is_valid, violations_dict)
        """
        violations = {
            "capacity": [],
            "time_window": [],
            "total_time": False,
            "population_served": 0,
            "population_left": 0,
        }
        
        # Check capacity constraint
        total_population = sum(self.nodes[node_id].get("population", 0) for node_id in path)
        vehicle_capacity = self.config["vehicle_capacity"]
        
        if total_population > vehicle_capacity:
            violations["capacity"].append({
                "population": total_population,
                "capacity": vehicle_capacity,
                "overflow": total_population - vehicle_capacity
            })
        
        violations["population_served"] = min(total_population, vehicle_capacity)
        violations["population_left"] = max(0, total_population - vehicle_capacity)
        
        # Check time window constraints
        current_time = 0
        for i, node_id in enumerate(path):
            node = self.nodes[node_id]
            zone = node["zone"]
            zone_meta = self.zone_metadata.get(zone, {})
            time_window = zone_meta.get("time_window", {"min": 0, "max": 999})
            
            if current_time < time_window["min"] or current_time > time_window["max"]:
                violations["time_window"].append({
                    "node": node_id,
                    "zone": zone,
                    "arrival_time": current_time,
                    "window": time_window
                })
            
            # Add edge cost as time
            if i < len(path) - 1:
                next_node = path[i + 1]
                edge = self._find_edge(node_id, next_node)
                if edge:
                    current_time += edge["cost"]
        
        # Check total time limit
        if current_time > self.config["time_limit"]:
            violations["total_time"] = True
        
        is_valid = (
            len(violations["capacity"]) == 0 and
            len(violations["time_window"]) == 0 and
            not violations["total_time"]
        )
        
        return is_valid, violations
    
    def _find_edge(self, from_id: int, to_id: int) -> Dict:
        """Find edge between two nodes"""
        for edge in self.graph_data["edges"]:
            if edge["from"] == from_id and edge["to"] == to_id:
                return edge
        return None
    
    def calculate_penalty(self, violations: Dict) -> float:
        """Calculate penalty score for constraint violations"""
        penalty = 0.0
        
        # Capacity violation penalty
        for cap_violation in violations["capacity"]:
            penalty += cap_violation["overflow"] * 10
        
        # Time window violation penalty
        for tw_violation in violations["time_window"]:
            time_diff = min(
                abs(tw_violation["arrival_time"] - tw_violation["window"]["min"]),
                abs(tw_violation["arrival_time"] - tw_violation["window"]["max"])
            )
            penalty += time_diff * 20
        
        # Total time violation
        if violations["total_time"]:
            penalty += 500
        
        return penalty


class MultiVehicleRouter:
    """Handles multi-vehicle routing for capacity-constrained problems"""
    
    def __init__(self, graph_data: Dict, config: Dict):
        self.graph_data = graph_data
        self.config = config
        self.nodes = {n["id"]: n for n in graph_data["nodes"]}
        
    def plan_multi_vehicle_routes(self, single_path: List[int]) -> List[Dict]:
        """
        Given a single path, split into multiple vehicle trips based on capacity
        
        Returns list of vehicle routes with population assignments
        """
        vehicle_capacity = self.config["vehicle_capacity"]
        num_vehicles = self.config["num_vehicles"]
        
        # Calculate cumulative population along path
        path_populations = []
        for node_id in single_path:
            pop = self.nodes[node_id].get("population", 0)
            path_populations.append({"node_id": node_id, "population": pop})
        
        # Greedy assignment to vehicles
        vehicles = []
        current_vehicle = {"id": 0, "route": [], "population": 0, "nodes": []}
        
        for node_data in path_populations:
            if current_vehicle["population"] + node_data["population"] <= vehicle_capacity:
                # Add to current vehicle
                current_vehicle["nodes"].append(node_data["node_id"])
                current_vehicle["population"] += node_data["population"]
                current_vehicle["route"].append(node_data["node_id"])
            else:
                # Vehicle full, start new one
                if current_vehicle["route"]:
                    vehicles.append(current_vehicle)
                
                if len(vehicles) >= num_vehicles:
                    # Out of vehicles, mark overflow
                    break
                
                current_vehicle = {
                    "id": len(vehicles),
                    "route": [node_data["node_id"]],
                    "population": node_data["population"],
                    "nodes": [node_data["node_id"]]
                }
        
        # Add last vehicle
        if current_vehicle["route"] and len(vehicles) < num_vehicles:
            vehicles.append(current_vehicle)
        
        return vehicles
    
    def calculate_total_evacuation_time(self, vehicles: List[Dict]) -> float:
        """Calculate total time considering parallel vehicle operation"""
        if not vehicles:
            return float("inf")
        
        # In parallel operation, total time is max of all vehicle times
        max_time = 0
        for vehicle in vehicles:
            route = vehicle["route"]
            vehicle_time = 0
            
            for i in range(len(route) - 1):
                edge = self._find_edge(route[i], route[i + 1])
                if edge:
                    vehicle_time += edge["cost"]
            
            max_time = max(max_time, vehicle_time)
        
        return max_time
    
    def _find_edge(self, from_id: int, to_id: int) -> Dict:
        """Find edge between two nodes"""
        for edge in self.graph_data["edges"]:
            if edge["from"] == from_id and edge["to"] == to_id:
                return edge
        return None


def encode_constraints_as_qubo(graph_data: Dict, config: Dict, zone_metadata: Dict) -> np.ndarray:
    """
    Encode hard constraints as QUBO (Quadratic Unconstrained Binary Optimization) matrix
    
    This is the key for quantum optimization - constraints become energy terms
    in the Hamiltonian that quantum annealing minimizes.
    
    QUBO formulation:
    - Binary variables: x_i = 1 if node i is in path
    - Objective: minimize path_cost + constraint_penalties
    - Capacity: penalty if sum(population * x_i) > capacity
    - Time windows: penalty if arrival time violates windows
    """
    nodes = graph_data["nodes"]
    n = len(nodes)
    
    # Initialize QUBO matrix (n x n)
    Q = np.zeros((n, n))
    
    # Diagonal terms: individual node costs (population/capacity pressure)
    capacity = config["vehicle_capacity"]
    for i, node in enumerate(nodes):
        pop = node.get("population", 0)
        # Penalize overcapacity
        Q[i][i] = (pop / capacity) * config["constraint_penalty"]
    
    # Off-diagonal terms: pairwise interactions (edge costs + time penalties)
    for edge in graph_data["edges"]:
        i = edge["from"]
        j = edge["to"]
        
        if i < n and j < n:
            # Add edge cost
            Q[i][j] += edge["cost"]
            Q[j][i] += edge["cost"]  # Symmetric
            
            # Add risk penalty
            Q[i][j] += edge["risk"] * 0.5
            Q[j][i] += edge["risk"] * 0.5
    
    # Time window penalties (simplified - would need path reconstruction for exact)
    for i, node in enumerate(nodes):
        zone = node["zone"]
        zone_meta = zone_metadata.get(zone, {})
        time_window = zone_meta.get("time_window", {"min": 0, "max": 999})
        
        # Penalize zones with tight time windows more
        window_size = time_window["max"] - time_window["min"]
        if window_size < 15:  # Tight window
            Q[i][i] += config["constraint_penalty"] * 0.1
    
    return Q
