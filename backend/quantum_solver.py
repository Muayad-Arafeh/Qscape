import time
import random
from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import minimize

class PathCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, start: int, end: int) -> Tuple[List[int], float, bool]:
        key = (start, end)
        if key in self.cache:
            return self.cache[key], 0.0, True
        return None, 0.0, False
    
    def precompute_paths(self, graph_data: Dict, dijkstra_func):
        nodes = graph_data['nodes']
        for node in nodes:
            start_id = node['id']
            for target in nodes:
                end_id = target['id']
                if start_id != end_id:
                    path, cost = dijkstra_func(start_id, end_id, graph_data)
                    if cost != float('inf'):
                        self.cache[(start_id, end_id)] = (path, cost)


class GeneticAlgorithmSolver:
    def __init__(self, population_size=20, generations=10):
        self.population_size = population_size
        self.generations = generations
    
    def solve(self, start: int, end: int, graph_data: Dict) -> Tuple[List[int], float]:
        nodes = {node['id']: node for node in graph_data['nodes']}
        edges = graph_data['edges']
        
        adjacency = {node_id: [] for node_id in nodes}
        for edge in edges:
            adjacency[edge['from']].append((edge['to'], edge['cost']))
        
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
                    return float('inf')
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
            return [start, end], float('inf')
        
        for generation in range(self.generations):
            population = sorted(population, key=lambda p: path_cost(p))
            population = population[:self.population_size // 2]
            
            while len(population) < self.population_size:
                parent1 = random.choice(population)
                parent2 = random.choice(population)
                
                if len(parent1) > 1 and len(parent2) > 1:
                    point = random.randint(1, min(len(parent1), len(parent2)) - 1)
                    child = parent1[:point] + parent2[point:]
                    
                    if random.random() < 0.1 and len(child) > 2:
                        idx = random.randint(1, len(child) - 2)
                        child = child[:idx] + child[idx + 1:]
                    
                    population.append(child)
        
        best_path = min(population, key=lambda p: path_cost(p))
        best_cost = path_cost(best_path)
        
        return best_path, best_cost


class QuantumSolver:
    def __init__(self):
        self.qaoa_implemented = self._check_qiskit()
    
    def _check_qiskit(self) -> bool:
        try:
            from qiskit import QuantumCircuit, QuantumRegister
            from qiskit_aer import Aer
            return True
        except ImportError:
            return False
    
    def solve(self, start: int, end: int, graph_data: Dict) -> Tuple[List[int], float]:
        if not self.qaoa_implemented:
            return self._quantum_annealing_simulation(start, end, graph_data)
        
        path, cost = self._qaoa_solver(start, end, graph_data)
        if cost == float('inf'):
            return self._quantum_annealing_simulation(start, end, graph_data)
        return path, cost
    
    def _quantum_annealing_simulation(self, start: int, end: int, graph_data: Dict) -> Tuple[List[int], float]:
        nodes = {node['id']: node for node in graph_data['nodes']}
        edges = graph_data['edges']
        
        adjacency = {node_id: [] for node_id in nodes}
        for edge in edges:
            adjacency[edge['from']].append((edge['to'], edge['cost']))
        
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
                    return float('inf')
            return total

        def bfs_initial_path(start_id, end_id):
            from collections import deque
            queue = deque([(start_id, [start_id])])
            visited = {start_id}
            while queue:
                current, path = queue.popleft()
                if current == end_id:
                    return path
                for neighbor, _ in adjacency[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            return None
        
        num_qubits = len(nodes)
        best_path = None
        best_cost = float('inf')
        num_iterations = 100
        temperature = 1.0
        cooling_rate = 0.95
        
        initial_path = bfs_initial_path(start, end)
        if not initial_path:
            return [start, end], float('inf')

        current_path = initial_path
        current_cost = path_cost(current_path)
        
        for iteration in range(num_iterations):
            candidate_path = self._generate_neighbor_path(current_path, adjacency, start, end)
            candidate_cost = path_cost(candidate_path)
            if candidate_cost == float('inf'):
                continue
            
            delta_e = candidate_cost - current_cost
            
            if delta_e < 0 or random.random() < np.exp(-delta_e / temperature):
                current_path = candidate_path
                current_cost = candidate_cost
            
            if current_cost < best_cost:
                best_path = current_path
                best_cost = current_cost
            
            temperature *= cooling_rate
        
        if best_cost == float('inf'):
            fallback_cost = path_cost(initial_path)
            return initial_path, fallback_cost

        return best_path if best_path else initial_path, best_cost
    
    def _generate_neighbor_path(self, path: List[int], adjacency: Dict, start: int, end: int) -> List[int]:
        new_path = path.copy()
        
        operation = random.choice(['insert', 'remove', 'swap'])
        
        if operation == 'insert' and len(new_path) < 10:
            insert_pos = random.randint(1, len(new_path) - 1)
            possible_nodes = list(adjacency.keys())
            if possible_nodes:
                new_node = random.choice(possible_nodes)
                new_path.insert(insert_pos, new_node)
        
        elif operation == 'remove' and len(new_path) > 2:
            remove_pos = random.randint(1, len(new_path) - 2)
            new_path.pop(remove_pos)
        
        elif operation == 'swap' and len(new_path) > 2:
            pos1 = random.randint(1, len(new_path) - 2)
            pos2 = random.randint(1, len(new_path) - 2)
            new_path[pos1], new_path[pos2] = new_path[pos2], new_path[pos1]
        
        return new_path
    
    def _qaoa_solver(self, start: int, end: int, graph_data: Dict) -> Tuple[List[int], float]:
        try:
            from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
            from qiskit_aer import Aer
            from qiskit_aer.primitives import Sampler
        except ImportError:
            return self._quantum_annealing_simulation(start, end, graph_data)
        
        num_qubits = min(len(graph_data['nodes']), 8)
        
        qr = QuantumRegister(num_qubits)
        cr = ClassicalRegister(num_qubits)
        circuit = QuantumCircuit(qr, cr)
        
        for i in range(num_qubits):
            circuit.h(qr[i])
        
        circuit.barrier()
        
        for i in range(num_qubits - 1):
            circuit.cx(qr[i], qr[i + 1])
        
        circuit.barrier()
        
        for i in range(num_qubits):
            circuit.measure(qr[i], cr[i])
        
        simulator = Aer.get_backend('qasm_simulator')
        job = simulator.run(circuit, shots=100)
        result = job.result()
        counts = result.get_counts(circuit)
        
        best_bitstring = max(counts, key=counts.get)
        path = [start]
        
        nodes = sorted([n['id'] for n in graph_data['nodes']])
        for i, bit in enumerate(best_bitstring):
            if bit == '1' and i < len(nodes):
                path.append(nodes[i])
        
        if end not in path:
            path.append(end)
        
        adjacency = {node['id']: [] for node in graph_data['nodes']}
        for edge in graph_data['edges']:
            adjacency[edge['from']].append((edge['to'], edge['cost']))
        
        def path_cost(p):
            total = 0
            for i in range(len(p) - 1):
                found = False
                for neighbor, cost in adjacency[p[i]]:
                    if neighbor == p[i + 1]:
                        total += cost
                        found = True
                        break
                if not found:
                    return float('inf')
            return total
        
        cost = path_cost(path)
        if cost == float('inf'):
            fallback_path = self._bfs_path(start, end, adjacency)
            if fallback_path:
                return fallback_path, path_cost(fallback_path)
        return path, cost

    def _bfs_path(self, start_id: int, end_id: int, adjacency: Dict) -> List[int] | None:
        from collections import deque
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        while queue:
            current, path = queue.popleft()
            if current == end_id:
                return path
            for neighbor, _ in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None
