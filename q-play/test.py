from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

q= QuantumRegister(3)
c= ClassicalRegister(3)
qc= QuantumCircuit(q, c)
qc.measure(q,c)

print(qc.draw())
print(qc.count())
