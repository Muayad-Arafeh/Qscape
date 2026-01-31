from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0,1)
qc.measure_all()

simulator = Aer.get_backend('qasm_simulator')
tqc = transpile(qc, simulator)
result = simulator.run(tqc, shots=1024).result()
print(result.get_counts())
print("Test file executed successfully.")