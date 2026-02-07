from typing import Dict, List, Tuple

from .objective import ObjectiveWeights, calculate_edge_cost


def dynamic_programming(
    start: int,
    end: int,
    graph_data: Dict,
    avoid_hazards: bool = False,
    distance_weight: float = 1.0,
    risk_weight: float = 0.0,
    hazard_weight: float = 0.0,
    congestion_weight: float = 0.0,
) -> Tuple[List[int], float]:
    """
    Dynamic Programming approach using Bellman-Ford relaxation.
    Finds shortest path by relaxing edges multiple times.
    Works on general graphs (including those with cycles).
    """
    nodes = {node["id"]: node for node in graph_data["nodes"]}
    edges = graph_data["edges"]

    if nodes.get(start, {}).get("blocked") or nodes.get(end, {}).get("blocked"):
        return [start, end], float("inf"), 0

    # Initialize distances and parents
    distances = {node_id: float("inf") for node_id in nodes}
    distances[start] = 0.0
    parent = {node_id: None for node_id in nodes}

    # Build adjacency with shared multi-objective logic
    weights = ObjectiveWeights(
        distance_weight=distance_weight,
        risk_weight=risk_weight,
        hazard_weight=hazard_weight,
        congestion_weight=congestion_weight,
    )
    adjacency = {}
    for edge in edges:
        if edge.get("blocked"):
            continue

        from_id = edge["from"]
        to_id = edge["to"]
        from_node = nodes.get(from_id)
        to_node = nodes.get(to_id)

        if from_node.get("blocked") or to_node.get("blocked"):
            continue

        # Skip hazardous paths if requested
        if avoid_hazards and (from_node.get("hazard") or to_node.get("hazard") or edge.get("hazard")):
            continue

        cost = calculate_edge_cost(edge, from_node, to_node, weights)

        if from_id not in adjacency:
            adjacency[from_id] = []
        adjacency[from_id].append((to_id, cost))

    # Relax edges |V| - 1 times
    num_nodes = len(nodes)
    evaluated_states = 0
    for _ in range(num_nodes - 1):
        for from_id in adjacency:
            for to_id, cost in adjacency[from_id]:
                evaluated_states += 1
                if distances[from_id] != float("inf") and distances[from_id] + cost < distances[to_id]:
                    distances[to_id] = distances[from_id] + cost
                    parent[to_id] = from_id

    # Reconstruct path
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()

    # If no path found, return empty path with infinity cost
    if path[0] != start:
        return [start, end], float("inf"), evaluated_states

    return path, distances[end], evaluated_states
