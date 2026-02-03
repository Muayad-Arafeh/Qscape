from typing import Dict, List


def build_adjacency(
    graph_data: Dict,
    avoid_hazards: bool,
    risk_weight: float,
    hazard_weight: float,
) -> Dict[int, List[tuple]]:
    nodes = {node["id"]: node for node in graph_data["nodes"]}
    adjacency = {node_id: [] for node_id in nodes}

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

        hazard_penalty = 0.0
        if from_node.get("hazard") or to_node.get("hazard") or edge.get("hazard"):
            hazard_penalty = hazard_weight

        cost = edge["cost"] + (risk_weight * edge.get("risk", 0.0)) + hazard_penalty
        adjacency[from_id].append((to_id, cost))

    return adjacency


def dijkstra(
    start: int,
    end: int,
    graph_data: Dict,
    avoid_hazards: bool = False,
    risk_weight: float = 0.0,
    hazard_weight: float = 0.0,
) -> tuple:
    nodes = {node["id"]: node for node in graph_data["nodes"]}

    if nodes.get(start, {}).get("blocked") or nodes.get(end, {}).get("blocked"):
        return [start, end], float("inf")
    adjacency = build_adjacency(
        graph_data,
        avoid_hazards,
        risk_weight,
        hazard_weight,
    )

    distances = {node_id: float("inf") for node_id in nodes}
    distances[start] = 0
    parent = {node_id: None for node_id in nodes}
    pq = [(0, start)]

    while pq:
        current_dist, current = heapq.heappop(pq)

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

    return path, distances[end]


import heapq
