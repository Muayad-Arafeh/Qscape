import random
from qiskit_aer import Aer
from qiskit.primitives import BackendSamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

# -----------------------------
# 1. Generate a realistic 24-node graph
# -----------------------------
num_nodes = 24
edges = []
costs = {}

# Connect each node to 2-3 random next nodes
for i in range(num_nodes - 1):
    num_edges = random.randint(2, 3)
    possible_targets = list(range(i+1, num_nodes))
    targets = random.sample(possible_targets, min(num_edges, len(possible_targets)))
    for t in targets:
        edge = f"x{i}{t}"
        edges.append(edge)
        costs[edge] = random.randint(1, 10)  # random travel cost

# -----------------------------
# 2. Define QUBO problem
# -----------------------------
qp = QuadraticProgram()
for e in edges:
    qp.binary_var(name=e)
qp.minimize(linear=costs)

# -----------------------------
# 3. Add connectivity constraints
# -----------------------------
# Start node (0)
start_edges = [e for e in edges if e.startswith("x0")]
qp.linear_constraint(linear={e:1 for e in start_edges}, sense="==", rhs=1, name="start")

# End node (23)
end_edges = [e for e in edges if e.endswith("23")]
qp.linear_constraint(linear={e:1 for e in end_edges}, sense="==", rhs=1, name="end")

# Node flow constraints for intermediate nodes
for n in range(1, num_nodes-1):
    incoming = [e for e in edges if e[1:] == str(n) or e[1:]==str(n).zfill(2)]
    outgoing = [e for e in edges if e[1:].startswith(str(n))]
    if incoming and outgoing:
        constraint = {e:1 for e in incoming}
        constraint.update({e:-1 for e in outgoing})
        qp.linear_constraint(linear=constraint, sense="==", rhs=0, name=f"node{n}_flow")

# -----------------------------
# 4. Solve with QAOA
# -----------------------------
pass_manager = generate_preset_pass_manager(
    optimization_level=1,
    basis_gates=["rz", "sx", "x", "cx", "measure"],
)
backend = Aer.get_backend("aer_simulator")
backend.set_options(method="matrix_product_state")
optimizer = COBYLA()
sampler = BackendSamplerV2(backend=backend, options={"default_shots": 512})

qaoa = QAOA(optimizer=optimizer, reps=1, sampler=sampler, transpiler=pass_manager)
solver = MinimumEigenOptimizer(qaoa)
result = solver.solve(qp)

# -----------------------------
# 5. Output result
# -----------------------------
print("Quantum solution:")
print(result)

print("\nSelected edges (evacuation path):")
for var, val in result.variables_dict.items():
    if val == 1:
        print(var)
