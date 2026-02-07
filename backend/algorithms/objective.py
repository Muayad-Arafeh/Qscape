from typing import Dict, List
from pydantic import BaseModel, Field


class ObjectiveWeights(BaseModel):
    """Weights for multi-objective cost function."""
    time_weight: float = Field(default=1.0, description="Weight for travel time cost")
    distance_weight: float = Field(default=1.0, description="Weight for base distance")
    risk_weight: float = Field(default=0.5, description="Weight for risk factor")
    hazard_weight: float = Field(default=0.7, description="Weight for hazard probability")
    congestion_weight: float = Field(default=0.5, description="Weight for congestion")


def calculate_edge_cost(
    edge: Dict,
    from_node: Dict,
    to_node: Dict,
    weights: ObjectiveWeights,
) -> float:
    """
    Compute multi-objective cost for a single edge using node penalties.
    """
    base_distance = edge.get("base_distance", edge.get("cost", 0.0))
    risk_level = (from_node.get("risk_level", 0.0) + to_node.get("risk_level", 0.0)) / 2
    hazard_prob = (from_node.get("hazard_probability", 0.0) + to_node.get("hazard_probability", 0.0)) / 2
    congestion = (from_node.get("congestion_score", 0.0) + to_node.get("congestion_score", 0.0)) / 2

    distance_weight = weights.distance_weight if weights.distance_weight is not None else weights.time_weight

    return (
        distance_weight * base_distance
        + weights.risk_weight * risk_level
        + weights.hazard_weight * hazard_prob
        + weights.congestion_weight * congestion
    )


def calculate_combined_cost(
    path: List[int],
    graph_data: Dict,
    weights: ObjectiveWeights,
) -> float:
    """
    Calculate combined cost for a path using weighted objective:
    C = w_d·distance + w_r·risk + w_h·hazard + w_c·congestion
    
    Args:
        path: List of node IDs in the path
        graph_data: Graph with nodes and edges
        weights: ObjectiveWeights object with α, β, γ
    
    Returns:
        Combined cost
    """
    if not path or len(path) < 2:
        return float("inf")

    edges_by_key = {}
    for edge in graph_data["edges"]:
        key = (edge["from"], edge["to"])
        edges_by_key[key] = edge

    nodes = {node["id"]: node for node in graph_data["nodes"]}

    total_cost = 0.0

    for i in range(len(path) - 1):
        from_id = path[i]
        to_id = path[i + 1]
        key = (from_id, to_id)

        if key not in edges_by_key:
            return float("inf")

        edge = edges_by_key[key]

        from_node = nodes.get(from_id, {})
        to_node = nodes.get(to_id, {})
        total_cost += calculate_edge_cost(edge, from_node, to_node, weights)

    return total_cost


def calculate_time_only_cost(path: List[int], graph_data: Dict) -> float:
    """
    Classic shortest path cost (time only, no risk/hazard).
    Used for benchmark comparison.
    """
    weights = ObjectiveWeights(distance_weight=1.0, risk_weight=0.0, hazard_weight=0.0, congestion_weight=0.0)
    return calculate_combined_cost(path, graph_data, weights)


def calculate_risk_aware_cost(
    path: List[int],
    graph_data: Dict,
    time_weight: float = 1.0,
    risk_weight: float = 0.5,
) -> float:
    """
    Risk-aware cost combining time and risk.
    Used for evacuation scenarios prioritizing safety.
    """
    weights = ObjectiveWeights(
        distance_weight=time_weight,
        risk_weight=risk_weight,
        hazard_weight=0.7,
        congestion_weight=0.5,
    )
    return calculate_combined_cost(path, graph_data, weights)
