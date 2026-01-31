from qiskit_aer import Aer
from qiskit_aer.primitives import SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

# -----------------------------
# 1. Define QUBO problem
# -----------------------------
qp = QuadraticProgram()

# Binary variables for edges
edges = ["x01", "x02", "x13", "x24", "x35", "x45"]
costs = {"x01":3, "x02":1, "x13":2, "x24":4, "x35":3, "x45":1}

for e in edges:
    qp.binary_var(name=e)

# Objective: minimize total cost
qp.minimize(linear=costs)

# -----------------------------
# 2. Constraints to ensure connected path
# -----------------------------

# Start node 0: one outgoing edge
qp.linear_constraint(linear={"x01":1, "x02":1}, sense="==", rhs=1, name="start")

# End node 5: one incoming edge
qp.linear_constraint(linear={"x35":1, "x45":1}, sense="==", rhs=1, name="end")

# Node 1: incoming == outgoing
qp.linear_constraint(linear={"x01":1, "x13":-1}, sense="==", rhs=0, name="node1_flow")

# Node 2: incoming == outgoing
qp.linear_constraint(linear={"x02":1, "x24":-1}, sense="==", rhs=0, name="node2_flow")

# Node 3: incoming == outgoing
qp.linear_constraint(linear={"x13":1, "x35":-1}, sense="==", rhs=0, name="node3_flow")

# Node 4: incoming == outgoing
qp.linear_constraint(linear={"x24":1, "x45":-1}, sense="==", rhs=0, name="node4_flow")

# -----------------------------
# 3. Solve with QAOA
# -----------------------------
backend = Aer.get_backend("aer_simulator")
pass_manager = generate_preset_pass_manager(backend=backend)
optimizer = COBYLA()
sampler = SamplerV2()

qaoa = QAOA(optimizer=optimizer, reps=2, sampler=sampler, transpiler=pass_manager)
solver = MinimumEigenOptimizer(qaoa)
result = solver.solve(qp)

# -----------------------------
# 4. Output result
# -----------------------------
print("Quantum solution:")
print(result)

print("\nSelected edges:")
for var, val in result.variables_dict.items():
    if val == 1:
        print(var)
