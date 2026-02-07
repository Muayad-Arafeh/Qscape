import heapq
import math
from typing import Dict, List, Tuple

from .objective import ObjectiveWeights, calculate_edge_cost


def astar(
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
    A* algorithm with Euclidean distance heuristic.
    Combines actual cost (g) with heuristic estimate (h) to find shortest paths faster.
    Heuristic: Euclidean distance from node to end node based on x,y coordinates.
    """
    nodes = {node["id"]: node for node in graph_data["nodes"]}
    edges = graph_data["edges"]

    if nodes.get(start, {}).get("blocked") or nodes.get(end, {}).get("blocked"):
        return [start, end], float("inf"), 0

    # Precompute node coordinates for heuristic
    node_coords = {node["id"]: (node["x"], node["y"]) for node in graph_data["nodes"]}

    def heuristic(node_id: int) -> float:
        """Euclidean distance from node to end node."""
        x1, y1 = node_coords.get(node_id, (0, 0))
        x2, y2 = node_coords.get(end, (0, 0))
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

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

    # A* priority queue: (f_score, counter, node_id)
    counter = 0
    open_set = [(heuristic(start), counter, start)]
    counter += 1

    # Track visited nodes
    g_score = {node_id: float("inf") for node_id in nodes}
    g_score[start] = 0.0
    parent = {node_id: None for node_id in nodes}
    closed_set = set()
    evaluated_states = 0

    while open_set:
        _, _, current = heapq.heappop(open_set)
        evaluated_states += 1

        if current in closed_set:
            continue

        if current == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path, g_score[end], evaluated_states

        closed_set.add(current)

        # Explore neighbors
        for neighbor, cost in adjacency.get(current, []):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + cost

            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent[neighbor] = current
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(open_set, (f_score, counter, neighbor))
                counter += 1

    # No path found
    return [start, end], float("inf"), evaluated_states
