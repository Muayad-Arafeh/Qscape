import random
from typing import Dict, List, Tuple


class GeneticAlgorithmSolver:
    def __init__(self, population_size=20, generations=10):
        self.population_size = population_size
        self.generations = generations

    def solve(self, start: int, end: int, graph_data: Dict, avoid_hazards: bool = False) -> Tuple[List[int], float]:
        nodes = {node["id"]: node for node in graph_data["nodes"]}
        edges = graph_data["edges"]

        if nodes.get(start, {}).get("blocked") or nodes.get(end, {}).get("blocked"):
            return [start, end], float("inf")

        adjacency = {node_id: [] for node_id in nodes}
        for edge in edges:
            if edge.get("blocked"):
                continue
            
            from_node = nodes.get(edge["from"])
            to_node = nodes.get(edge["to"])

            if from_node.get("blocked") or to_node.get("blocked"):
                continue
            
            # Skip hazardous paths if requested
            if avoid_hazards and (from_node.get("hazard") or to_node.get("hazard") or edge.get("hazard")):
                continue
            
            adjacency[edge["from"]].append((edge["to"], edge["cost"]))

        def path_cost(path):
            total = 0
            for i in range(len(path) - 1):
                found = False
                for neighbor, cost in adjacency[path[i]]:
                    if neighbor == path[i + 1]:
                        total += cost
                        found = True
                        break
                if not found:
                    return float("inf")
            return total

        def generate_random_path():
            if start == end:
                return [start]

            path = [start]
            current = start
            visited = {start}
            max_attempts = len(nodes) * 2
            attempts = 0

            while current != end and attempts < max_attempts:
                neighbors = [n for n, _ in adjacency[current] if n not in visited or n == end]
                if neighbors:
                    if end in neighbors and random.random() > 0.3:
                        path.append(end)
                        current = end
                    else:
                        next_node = random.choice(neighbors)
                        path.append(next_node)
                        visited.add(next_node)
                        current = next_node
                else:
                    break
                attempts += 1

            if current == end:
                return path
            return None

        population = []
        for _ in range(self.population_size):
            path = generate_random_path()
            if path:
                population.append(path)

        if not population:
            return [start, end], float("inf")

        for _ in range(self.generations):
            population = sorted(population, key=lambda p: path_cost(p))
            population = population[: self.population_size // 2]

            while len(population) < self.population_size:
                parent1 = random.choice(population)
                parent2 = random.choice(population)

                if len(parent1) > 1 and len(parent2) > 1:
                    point = random.randint(1, min(len(parent1), len(parent2)) - 1)
                    child = parent1[:point] + parent2[point:]

                    if random.random() < 0.1 and len(child) > 2:
                        idx = random.randint(1, len(child) - 2)
                        child = child[:idx] + child[idx + 1 :]

                    population.append(child)

        best_path = min(population, key=lambda p: path_cost(p))
        best_cost = path_cost(best_path)

        return best_path, best_cost
