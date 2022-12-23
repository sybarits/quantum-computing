from hello_qiskit import run_puzzle
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

def initialize_program():
    qubit = QuantumRegister(2)
    A = qubit[0]
    B = qubit[1]
    
    bit = ClassicalRegister(2)
    a = bit[0]
    b = bit[1]
    
    qc = QuantumCircuit(qubit, bit)
    
    return A, B, a, b, qc


def hash2bit(variable, hash_type, bit, qc):
    if hash_type == 'H':
        qc.h(variable)
    qc.measure(variable, bit)

puzzle = run_puzzle(12)

import numpy as np
def setup_variables(A, B, qc):
    for line in puzzle.program:
        eval(line)


shots = 8192
from qiskit import assemble, transpile

def calculate_P(backend):
    P = {}
    program = {}
    for hashes in ['VV','VH','HV','HH']:

        A, B, a, b, program[hashes] = initialize_program()

        setup_variables(A, B, program[hashes])

        hash2bit(A, hashes[0], a, program[hashes])
        hash2bit(B, hashes[1], b, program[hashes])

    # submit jobs
    t_qcs = transpile(list(program.values()), backend)
    qobj = assemble(t_qcs, shots=shots)
    job = backend.run(qobj)

    # get the results
    for hashes in ['VV','VH','HV','HH']:
        stats = job.result().get_counts(program[hashes])

        P[hashes] = 0
        for string in stats.keys():
            a = string[-1]
            b = string[-2]

            if a != b:
                P[hashes] += stats[string] / shots

    return P


def bell_test(P):
    sum_P = sum(P.values())
    for hashes in P:

        bound = sum_P - P[hashes]

        print("The upper bound for P['"+hashes+"'] is "+str(bound))
        print("The value of P['"+hashes+"'] is "+str(P[hashes]))
        if P[hashes]<=bound:
            print("The upper bound is obeyed :)\n")
        else:
            if P[hashes]-bound < 0.1:
                print("This seems to have gone over the upper bound, "
                      "but only by a little bit :S\nProbably just rounding"
                      " errors or statistical noise.\n")
            else:
                print("This has gone well over the upper bound :O !!!!!\n")



from qiskit import Aer
backend = Aer.get_backend('aer_simulator')


P = calculate_P(backend)
print(P)


bell_test(P)

