import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import IBMQ, Aer, transpile, assemble
from qiskit.visualization import plot_histogram, plot_bloch_multivector, array_to_latex
from qiskit.extensions import Initialize
#from qiskit.ignis.verification import marginal_counts
from qiskit.result import marginal_counts
from qiskit.quantum_info import random_statevector


def create_bell_pair(qc, a, b):
    """Creates a bell pair in qc using qubits a & b"""
    qc.h(a) # Put qubit a into state |+>
    qc.cx(a,b) # CNOT with a as control and b as target

def alice_gates(qc, psi, a):
    qc.cx(psi, a)
    qc.h(psi)

def measure_and_send(qc, a, b):
    """Measures qubits a & b and 'sends' the results to Bob"""
    qc.barrier()
    qc.measure(a,0)
    qc.measure(b,1)

# This function takes a QuantumCircuit (qc), integer (qubit)
# and ClassicalRegisters (crz & crx) to decide which gates to apply
def bob_gates(qc, qubit, crz, crx):
    # Here we use c_if to control our gates with a classical
    # bit instead of a qubit
    qc.x(qubit).c_if(crx, 1) # Apply gates if the registers
    qc.z(qubit).c_if(crz, 1) # are in the state '1'

# Create random 1-qubit state
psi = random_statevector(2)
print('before circuit: {}'.format(psi)) 

init_gate = Initialize(psi)
init_gate.label = "init"

inverse_init_gate = init_gate.gates_to_uncompute()

qr = QuantumRegister(3, name="q")   # Protocol uses 3 qubits
crz = ClassicalRegister(1, name="crz") # and 2 classical registers
crx = ClassicalRegister(1, name="crx") # in 2 different registers
qc = QuantumCircuit(qr, crz, crx)

## STEP 0
# First, let's initialize Alice's q0
qc.append(init_gate, [0])
qc.barrier()

## STEP 1
# Now begins the teleportation protocol
create_bell_pair(qc, 1, 2)
qc.barrier()

## STEP 2
# Send q1 to Alice and q2 to Bob
alice_gates(qc, 0, 1)

## STEP 3
# Alice then sends her classical bits to Bob
measure_and_send(qc, 0, 1)

## STEP 4
# Bob decodes qubits
bob_gates(qc, 2, crz, crx)
qc.draw()

## STEP 5
# reverse the initialization process
qc.append(inverse_init_gate, [2])

# Need to add a new ClassicalRegister
# to see the result
cr_result = ClassicalRegister(1)
qc.add_register(cr_result)
qc.measure(2,2)

# Display the circuit
qc.draw()

# Get Backend
sim = Aer.get_backend('aer_simulator')

#qc.save_statevector()
#out_vector = sim.run(qc).result().get_statevector()
#plot_bloch_multivector(out_vector)

t_qc = transpile(qc, sim)
# t_qc.save_statevector()
for qubit in range(3):
    qubits_of_interest = [qubit]
    marginalised_results = marginal_counts(sim.run(t_qc).result(), indices=qubits_of_interest)
    marginalised_counts = marginalised_results.get_counts()
    print("qubit",qubit,"marginalised_counts", marginalised_counts)

counts = sim.run(t_qc).result().get_counts()
print("counts", counts)
qubit_counts = [marginal_counts(counts, [qubit]) for qubit in range(3)]
print("qubit_counts", qubit_counts)
#plot_histogram(qubit_counts)


