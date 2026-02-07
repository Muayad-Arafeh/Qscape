import heapq
from typing import Dict, List

from .objective import ObjectiveWeights, calculate_edge_cost


def build_adjacency(
    graph_data: Dict,
    avoid_hazards: bool,
    distance_weight: float,
    risk_weight: float,
    hazard_weight: float,
    congestion_weight: float,
) -> Dict[int, List[tuple]]:
    nodes = {node["id"]: node for node in graph_data["nodes"]}
    adjacency = {node_id: [] for node_id in nodes}

    weights = ObjectiveWeights(
        distance_weight=distance_weight,
        risk_weight=risk_weight,
        hazard_weight=hazard_weight,
        congestion_weight=congestion_weight,
    )

    for edge in graph_data["edges"]:
        if edge.get("blocked"):
            continue

        from_id = edge["from"]
        to_id = edge["to"]
        from_node = nodes.get(from_id)
        to_node = nodes.get(to_id)

        if from_node.get("blocked") or to_node.get("blocked"):
            continue

        if avoid_hazards and (from_node.get("hazard") or to_node.get("hazard") or edge.get("hazard")):
            continue

        cost = calculate_edge_cost(edge, from_node, to_node, weights)
        adjacency[from_id].append((to_id, cost))

    return adjacency


def dijkstra(
    start: int,
    end: int,
    graph_data: Dict,
    avoid_hazards: bool = False,
    distance_weight: float = 1.0,
    risk_weight: float = 0.0,
    hazard_weight: float = 0.0,
    congestion_weight: float = 0.0,
) -> tuple:
    nodes = {node["id"]: node for node in graph_data["nodes"]}

    if nodes.get(start, {}).get("blocked") or nodes.get(end, {}).get("blocked"):
        return [start, end], float("inf"), 0
    adjacency = build_adjacency(
        graph_data,
        avoid_hazards,
        distance_weight,
        risk_weight,
        hazard_weight,
        congestion_weight,
    )

    distances = {node_id: float("inf") for node_id in nodes}
    distances[start] = 0
    parent = {node_id: None for node_id in nodes}
    pq = [(0, start)]
    evaluated_states = 0

    while pq:
        current_dist, current = heapq.heappop(pq)
        evaluated_states += 1

        if current_dist > distances[current]:
            continue

        if current == end:
            break

        for neighbor, cost in adjacency[current]:
            new_dist = current_dist + cost

            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parent[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))

    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()

    return path, distances[end], evaluated_states

