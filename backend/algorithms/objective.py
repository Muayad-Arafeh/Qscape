from typing import Dict, List
from pydantic import BaseModel, Field


class ObjectiveWeights(BaseModel):
    """Weights for multi-objective cost function."""
    time_weight: float = Field(default=1.0, description="Weight for travel time cost")
    risk_weight: float = Field(default=0.5, description="Weight for risk factor")
    hazard_weight: float = Field(default=2.0, description="Weight for hazard penalty")


def calculate_combined_cost(
    path: List[int],
    graph_data: Dict,
    weights: ObjectiveWeights,
) -> float:
    """
    Calculate combined cost for a path using weighted objective:
    C = α·(time cost) + β·(risk cost) + γ·(hazard penalty)
    
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

    total_cost = 0.0

    for i in range(len(path) - 1):
        from_id = path[i]
        to_id = path[i + 1]
        key = (from_id, to_id)

        if key not in edges_by_key:
            return float("inf")

        edge = edges_by_key[key]

        # Time component
        time_cost = edge["cost"] * weights.time_weight

        # Risk component
        risk_cost = edge.get("risk", 0.0) * weights.risk_weight

        # Hazard penalty
        hazard_penalty = 0.0
        if edge.get("hazard") or edge.get("blocked"):
            hazard_penalty = weights.hazard_weight

        total_cost += time_cost + risk_cost + hazard_penalty

    return total_cost


def calculate_time_only_cost(path: List[int], graph_data: Dict) -> float:
    """
    Classic shortest path cost (time only, no risk/hazard).
    Used for benchmark comparison.
    """
    weights = ObjectiveWeights(time_weight=1.0, risk_weight=0.0, hazard_weight=0.0)
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
        time_weight=time_weight,
        risk_weight=risk_weight,
        hazard_weight=2.0
    )
    return calculate_combined_cost(path, graph_data, weights)
