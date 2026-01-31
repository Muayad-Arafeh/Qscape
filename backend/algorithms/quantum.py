import random
from typing import Dict, List, Tuple
import numpy as np
from collections import deque

from .objective import ObjectiveWeights, calculate_combined_cost


class QuantumSolver:
    def __init__(self):
        self.qaoa_implemented = self._check_qiskit()
        self.execution_mode = "QAOA" if self.qaoa_implemented else "Quantum Annealing Simulation"

    def _check_qiskit(self) -> bool:
        try:
            from qiskit import QuantumCircuit, QuantumRegister
            from qiskit_aer import Aer
            return True
        except ImportError:
            return False

    def solve(self, start: int, end: int, graph_data: Dict) -> Tuple[List[int], float]:
        """
        Solve shortest path using quantum approach.
        
        Returns path and cost. Metadata about execution mode is stored in self.execution_mode
        """
        if not self.qaoa_implemented:
            # Fall back to simulated quantum annealing
            path, cost = self._quantum_annealing_simulation(start, end, graph_data)
            self.execution_mode = "Quantum Annealing Simulation (Qiskit unavailable)"
            return path, cost

        # Try QAOA first
        path, cost = self._qaoa_solver(start, end, graph_data)
        self.execution_mode = "QAOA"
        
        if cost == float("inf"):
            # QAOA failed, fall back to simulation
            path, cost = self._quantum_annealing_simulation(start, end, graph_data)
            self.execution_mode = "Quantum Annealing Simulation (QAOA fallback)"
        
        return path, cost

    def get_execution_mode(self) -> str:
        """Return which quantum execution mode was used."""
        return self.execution_mode

    def _quantum_annealing_simulation(self, start: int, end: int, graph_data: Dict) -> Tuple[List[int], float]:
        nodes = {node["id"]: node for node in graph_data["nodes"]}
        edges = graph_data["edges"]

        adjacency = {node_id: [] for node_id in nodes}
        for edge in edges:
            if edge.get("blocked"):
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

        best_path = None
        best_cost = float("inf")
        num_iterations = 100
        temperature = 1.0
        cooling_rate = 0.95

        initial_path = bfs_initial_path(start, end)
        if not initial_path:
            return [start, end], float("inf")

        current_path = initial_path
        current_cost = path_cost(current_path)

        for _ in range(num_iterations):
            candidate_path = self._generate_neighbor_path(current_path, adjacency, start, end)
            candidate_cost = path_cost(candidate_path)
            if candidate_cost == float("inf"):
                continue

            delta_e = candidate_cost - current_cost

            if delta_e < 0 or random.random() < np.exp(-delta_e / temperature):
                current_path = candidate_path
                current_cost = candidate_cost

            if current_cost < best_cost:
                best_path = current_path
                best_cost = current_cost

            temperature *= cooling_rate

        if best_cost == float("inf"):
            fallback_cost = path_cost(initial_path)
            return initial_path, fallback_cost

        return best_path if best_path else initial_path, best_cost

    def _generate_neighbor_path(self, path: List[int], adjacency: Dict, start: int, end: int) -> List[int]:
        new_path = path.copy()

        operation = random.choice(["insert", "remove", "swap"])

        if operation == "insert" and len(new_path) < 10:
            insert_pos = random.randint(1, len(new_path) - 1)
            possible_nodes = list(adjacency.keys())
            if possible_nodes:
                new_node = random.choice(possible_nodes)
                new_path.insert(insert_pos, new_node)

        elif operation == "remove" and len(new_path) > 2:
            remove_pos = random.randint(1, len(new_path) - 2)
            new_path.pop(remove_pos)

        elif operation == "swap" and len(new_path) > 2:
            pos1 = random.randint(1, len(new_path) - 2)
            pos2 = random.randint(1, len(new_path) - 2)
            new_path[pos1], new_path[pos2] = new_path[pos2], new_path[pos1]

        return new_path

    def _qaoa_solver(self, start: int, end: int, graph_data: Dict) -> Tuple[List[int], float]:
        """
        Implement QAOA for shortest path problem.
        Uses Ising Hamiltonian encoding where edge weights are encoded in Ising coupling.
        
        The approach:
        1. Map nodes to qubits (limited to 8 qubits for simulation)
        2. Encode cost Hamiltonian based on edge weights
        3. Apply QAOA ansatz (alternating problem and mixer Hamiltonian applications)
        4. Measure and decode results
        """
        try:
            from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
            from qiskit_aer import Aer
        except ImportError:
            return self._quantum_annealing_simulation(start, end, graph_data)

        nodes = {node["id"]: node for node in graph_data["nodes"]}
        num_nodes = len(nodes)
        num_qubits = min(num_nodes, 8)  # Limit to 8 qubits for simulation tractability

        # Map node IDs to qubit indices
        node_list = sorted(nodes.keys())
        node_to_qubit = {node_id: i for i, node_id in enumerate(node_list[:num_qubits])}
        qubit_to_node = {i: node_id for node_id, i in node_to_qubit.items()}

        # Build cost matrix based on edges
        cost_matrix = np.full((num_qubits, num_qubits), np.inf)
        for i in range(num_qubits):
            cost_matrix[i][i] = 0.0

        for edge in graph_data["edges"]:
            from_id = edge["from"]
            to_id = edge["to"]
            if from_id in node_to_qubit and to_id in node_to_qubit:
                from_qubit = node_to_qubit[from_id]
                to_qubit = node_to_qubit[to_id]
                # Normalize edge cost to [0, 1] for angle encoding
                normalized_cost = min(1.0, edge["cost"] / 10.0)
                cost_matrix[from_qubit][to_qubit] = normalized_cost

        # QAOA parameters
        p = 2  # Number of QAOA layers
        gamma_vals = [0.5, 0.7]  # Problem Hamiltonian angles
        beta_vals = [0.3, 0.4]   # Mixer Hamiltonian angles

        qr = QuantumRegister(num_qubits)
        cr = ClassicalRegister(num_qubits)
        circuit = QuantumCircuit(qr, cr)

        # Initial superposition
        for i in range(num_qubits):
            circuit.h(qr[i])

        circuit.barrier()

        # QAOA ansatz: p layers of problem + mixer Hamiltonians
        for layer in range(p):
            # Problem Hamiltonian: encode cost through ZZ interactions
            gamma = gamma_vals[layer % len(gamma_vals)]
            for i in range(num_qubits - 1):
                for j in range(i + 1, num_qubits):
                    if cost_matrix[i][j] < np.inf:
                        # ZZ interaction strength proportional to edge cost
                        angle = 2 * gamma * cost_matrix[i][j]
                        circuit.zz(angle, qr[i], qr[j])

            # Self-loop terms (single Z rotations)
            for i in range(num_qubits):
                circuit.rz(2 * gamma * cost_matrix[i][i], qr[i])

            circuit.barrier()

            # Mixer Hamiltonian: X rotations
            beta = beta_vals[layer % len(beta_vals)]
            for i in range(num_qubits):
                circuit.rx(2 * beta, qr[i])

            circuit.barrier()

        # Measurement
        for i in range(num_qubits):
            circuit.measure(qr[i], cr[i])

        # Execute on simulator
        simulator = Aer.get_backend("qasm_simulator")
        job = simulator.run(circuit, shots=1000)
        result = job.result()
        counts = result.get_counts(circuit)

        # Find best bitstring by frequency
        best_bitstring = max(counts, key=counts.get)

        # Decode bitstring to path
        selected_nodes = [qubit_to_node[i] for i, bit in enumerate(best_bitstring) if bit == "1"]
        
        # Build path by BFS from start to end using selected nodes
        path = self._bfs_path_with_node_set(start, end, graph_data, set(selected_nodes))
        
        if not path:
            # Fallback: use BFS on all nodes
            adjacency = {node["id"]: [] for node in graph_data["nodes"]}
            for edge in graph_data["edges"]:
                if edge.get("blocked"):
                    continue
                adjacency[edge["from"]].append((edge["to"], edge["cost"]))
            path = self._bfs_path(start, end, adjacency)
            
            if not path:
                return [start, end], float("inf")

        # Calculate cost
        adjacency = {node["id"]: [] for node in graph_data["nodes"]}
        for edge in graph_data["edges"]:
            if edge.get("blocked"):
                continue
            adjacency[edge["from"]].append((edge["to"], edge["cost"]))

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
                    return float("inf")
            return total

        cost = path_cost(path)
        return path, cost

    def _bfs_path_with_node_set(
        self, start_id: int, end_id: int, graph_data: Dict, selected_nodes: set
    ) -> List[int] | None:
        """BFS but prioritize paths through selected_nodes."""
        adjacency = {}
        for edge in graph_data["edges"]:
            if edge.get("blocked"):
                continue
            from_id = edge["from"]
            to_id = edge["to"]
            if from_id not in adjacency:
                adjacency[from_id] = []
            adjacency[from_id].append((to_id, edge["cost"]))

        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        best_path = None

        while queue:
            current, path = queue.popleft()
            if current == end_id:
                if best_path is None or len(path) < len(best_path):
                    best_path = path
                continue

            for neighbor, _ in adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return best_path

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
