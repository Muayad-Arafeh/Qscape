"""
AI Prediction Models for Qscape Routing System
Includes traffic prediction, hazard prediction, and route quality prediction
"""
import random
import math
from typing import Dict, List, Tuple
from datetime import datetime


class TrafficPredictor:
    """Predicts traffic congestion levels for nodes and edges"""
    
    def __init__(self, graph_data: dict):
        self.graph_data = graph_data
        
    def predict_traffic(self, hazard_nodes: List[int] = None, blocked_nodes: List[int] = None) -> Dict:
        """
        Predict traffic/congestion for all nodes and edges
        Returns capacity usage percentage (0-100%)
        
        Rule-based logic (can be replaced with trained ML model):
        - Higher traffic near hazard zones (people avoiding)
        - Lower traffic in blocked areas
        - Time-based patterns
        - Bottleneck detection (low capacity = high congestion)
        """
        hazard_nodes = hazard_nodes or []
        blocked_nodes = blocked_nodes or []
        current_hour = datetime.now().hour
        
        # Time-based multiplier (peak hours: 7-9, 16-18)
        peak_multiplier = 1.5 if current_hour in [7, 8, 9, 16, 17, 18] else 1.0
        
        node_traffic = {}
        edge_traffic = {}
        
        # Predict node traffic
        for node in self.graph_data['nodes']:
            node_id = node['id']
            capacity = node.get('capacity', 50)
            
            # Blocked nodes have zero traffic (no traffic flows through them)
            if node_id in blocked_nodes:
                node_traffic[node_id] = 0.0
                continue
            
            # Base traffic (inverse of capacity)
            base_traffic = (100 - capacity) * 0.5
            
            # Increase traffic if near hazards (people rerouting through)
            hazard_boost = 0
            for hazard_id in hazard_nodes:
                distance = self._get_node_distance(node_id, hazard_id)
                if distance < 3:  # Within 3 edges
                    hazard_boost += 20 * (3 - distance) / 3
            
            # Zone-based patterns
            zone = node.get('zone', 'A')
            zone_multiplier = {
                'A': 0.8,   # Entry zone - moderate
                'B': 1.3,   # Danger zone - high congestion
                'C': 0.9,   # Safe zone - low-moderate
                'EXIT': 0.7 # Exit zone - low
            }.get(zone, 1.0)
            
            # Calculate final traffic
            traffic = min(95, (base_traffic + hazard_boost) * zone_multiplier * peak_multiplier)
            node_traffic[node_id] = round(traffic, 1)
        
        # Predict edge traffic
        for edge in self.graph_data['edges']:
            source = edge['from']
            target = edge['to']
            capacity = edge.get('capacity', 25)
            
            # Base traffic (inverse of capacity)
            base_traffic = (50 - capacity) * 1.2
            
            # Average traffic of connected nodes
            avg_node_traffic = (node_traffic.get(source, 0) + node_traffic.get(target, 0)) / 2
            
            # Edge traffic is influenced by node traffic
            traffic = min(95, (base_traffic + avg_node_traffic * 0.4) * peak_multiplier)
            edge_traffic[f"{source}-{target}"] = round(traffic, 1)
        
        return {
            'nodes': node_traffic,
            'edges': edge_traffic,
            'peak_hour': current_hour in [7, 8, 9, 16, 17, 18],
            'prediction_time': datetime.now().isoformat()
        }
    
    def _get_node_distance(self, node1: int, node2: int) -> int:
        """Get shortest path distance between two nodes (BFS)"""
        if node1 == node2:
            return 0
        
        # Build adjacency list
        adj = {}
        for edge in self.graph_data['edges']:
            source = edge['from']
            target = edge['to']
            if source not in adj:
                adj[source] = []
            if target not in adj:
                adj[target] = []
            adj[source].append(target)
            adj[target].append(source)
        
        # BFS
        queue = [(node1, 0)]
        visited = {node1}
        
        while queue:
            current, dist = queue.pop(0)
            if current == node2:
                return dist
            
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return 999  # Not connected


class HazardPredictor:
    """Predicts probability of nodes becoming hazardous"""
    
    def __init__(self, graph_data: dict):
        self.graph_data = graph_data
    
    def predict_hazards(self, current_hazards: List[int] = None, blocked_nodes: List[int] = None) -> Dict:
        """
        Predict hazard probability for each node (0-100%)
        
        Rule-based logic (can be replaced with trained ML model):
        - Higher risk in danger zones (Zone B)
        - Risk spreads from existing hazards
        - Capacity constraints increase risk
        - Time-based patterns
        """
        current_hazards = current_hazards or []
        blocked_nodes = blocked_nodes or []
        current_hour = datetime.now().hour
        
        # Night hours are more dangerous (20-5)
        night_multiplier = 1.4 if current_hour >= 20 or current_hour <= 5 else 1.0
        
        hazard_predictions = {}
        
        for node in self.graph_data['nodes']:
            node_id = node['id']
            
            # Skip already hazardous or blocked nodes
            if node_id in current_hazards:
                hazard_predictions[node_id] = {'probability': 100.0, 'risk_level': 'ACTIVE'}
                continue
            if node_id in blocked_nodes:
                hazard_predictions[node_id] = {'probability': 0.0, 'risk_level': 'BLOCKED'}
                continue
            
            # Base risk by zone
            zone = node.get('zone', 'A')
            base_risk = {
                'A': 15,    # Entry - low risk
                'B': 45,    # Danger zone - high risk
                'C': 20,    # Safe zone - low-moderate risk
                'EXIT': 5   # Exit - very low risk
            }.get(zone, 25)
            
            # Capacity-based risk (lower capacity = higher risk of becoming hazard)
            capacity = node.get('capacity', 50)
            capacity_risk = (100 - capacity) * 0.3
            
            # Proximity to existing hazards (hazards spread)
            proximity_risk = 0
            for hazard_id in current_hazards:
                distance = self._get_node_distance(node_id, hazard_id)
                if distance < 4:
                    proximity_risk += 30 * (4 - distance) / 4
            
            # Random environmental factor
            environmental_factor = random.uniform(-5, 10)
            
            # Calculate total probability
            probability = min(95, (base_risk + capacity_risk + proximity_risk + environmental_factor) * night_multiplier)
            probability = max(0, probability)
            
            # Classify risk level
            if probability >= 70:
                risk_level = 'CRITICAL'
            elif probability >= 50:
                risk_level = 'HIGH'
            elif probability >= 30:
                risk_level = 'MODERATE'
            else:
                risk_level = 'LOW'
            
            hazard_predictions[node_id] = {
                'probability': round(probability, 1),
                'risk_level': risk_level
            }
        
        return {
            'predictions': hazard_predictions,
            'high_risk_nodes': [nid for nid, pred in hazard_predictions.items() if pred['probability'] >= 50],
            'night_time': night_multiplier > 1.0,
            'prediction_time': datetime.now().isoformat()
        }
    
    def _get_node_distance(self, node1: int, node2: int) -> int:
        """Get shortest path distance between two nodes (BFS)"""
        if node1 == node2:
            return 0
        
        # Build adjacency list
        adj = {}
        for edge in self.graph_data['edges']:
            source = edge['from']
            target = edge['to']
            if source not in adj:
                adj[source] = []
            if target not in adj:
                adj[target] = []
            adj[source].append(target)
            adj[target].append(source)
        
        # BFS
        queue = [(node1, 0)]
        visited = {node1}
        
        while queue:
            current, dist = queue.pop(0)
            if current == node2:
                return dist
            
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return 999


class RouteQualityPredictor:
    """Predicts route quality and success probability"""
    
    def __init__(self, graph_data: dict):
        self.graph_data = graph_data
    
    def predict_route_quality(self, start: int, end: int, hazard_nodes: List[int] = None,
                              blocked_nodes: List[int] = None, algorithm: str = 'dijkstra') -> Dict:
        """
        Predict route quality before expensive computation
        
        Returns:
        - success_probability: 0-100% chance of finding viable route
        - estimated_time: predicted execution time in ms
        - estimated_cost: predicted route cost
        - complexity_score: route complexity (0-100)
        - recommendation: should we compute this route?
        """
        hazard_nodes = hazard_nodes or []
        blocked_nodes = blocked_nodes or []
        
        # Calculate graph complexity
        total_nodes = len(self.graph_data['nodes'])
        total_edges = len(self.graph_data['edges'])
        connectivity = total_edges / (total_nodes * (total_nodes - 1) / 2)
        
        # Calculate obstacle density
        obstacle_count = len(hazard_nodes) + len(blocked_nodes)
        obstacle_density = (obstacle_count / total_nodes) * 100
        
        # Estimate straight-line distance
        start_node = next((n for n in self.graph_data['nodes'] if n['id'] == start), None)
        end_node = next((n for n in self.graph_data['nodes'] if n['id'] == end), None)
        
        if not start_node or not end_node:
            return {
                'success_probability': 0.0,
                'estimated_time': 0,
                'estimated_cost': 0,
                'complexity_score': 0,
                'recommendation': 'INVALID',
                'reason': 'Invalid start or end node'
            }
        
        # Euclidean distance (using x, y coordinates)
        x_diff = start_node['x'] - end_node['x']
        y_diff = start_node['y'] - end_node['y']
        straight_distance = math.sqrt(x_diff**2 + y_diff**2)
        
        # Check if start or end are blocked/hazards
        if start in blocked_nodes or end in blocked_nodes:
            return {
                'success_probability': 0.0,
                'estimated_time': 0,
                'estimated_cost': 999999,
                'complexity_score': 100,
                'recommendation': 'REJECT',
                'reason': 'Start or end node is blocked'
            }
        
        if start in hazard_nodes or end in hazard_nodes:
            success_probability = 20.0
        else:
            success_probability = 95.0
        
        # Reduce probability based on obstacles
        success_probability -= obstacle_density * 1.5
        success_probability = max(5, min(95, success_probability))
        
        # Estimate execution time based on algorithm and complexity
        base_time = {
            'dijkstra': 50,
            'astar': 40,
            'dynamic_programming': 60,
            'quantum': 80,
            'genetic': 100
        }.get(algorithm, 50)
        
        # Add constraint validation overhead (exponential for classical)
        path_estimate = straight_distance * 150  # Rough path length estimate
        if algorithm in ['dijkstra', 'astar', 'dynamic_programming', 'genetic']:
            # Cap path estimate to avoid overflow in exponential calculation
            capped_estimate = min(path_estimate / 3, 20)
            constraint_overhead = min(math.pow(2, capped_estimate) * 50, 5000)
        else:
            constraint_overhead = 0
        
        estimated_time = base_time + constraint_overhead + (obstacle_count * 5)
        
        # Estimate cost (proportional to distance and obstacles)
        estimated_cost = straight_distance * 120 + (obstacle_count * 10)
        
        # Complexity score
        complexity_score = min(100, (obstacle_density * 0.5 + straight_distance * 500 + (1 - connectivity) * 30))
        
        # Recommendation
        if success_probability < 20:
            recommendation = 'REJECT'
            reason = 'Low success probability - too many obstacles'
        elif complexity_score > 80 and algorithm in ['genetic']:
            recommendation = 'CAUTION'
            reason = 'High complexity - may take long time'
        elif estimated_time > 2000:
            recommendation = 'SLOW'
            reason = 'Estimated time > 2 seconds due to constraint validation'
        else:
            recommendation = 'PROCEED'
            reason = 'Good route quality expected'
        
        return {
            'success_probability': round(success_probability, 1),
            'estimated_time': round(estimated_time, 0),
            'estimated_cost': round(estimated_cost, 2),
            'complexity_score': round(complexity_score, 1),
            'recommendation': recommendation,
            'reason': reason,
            'obstacle_density': round(obstacle_density, 1),
            'prediction_time': datetime.now().isoformat()
        }
