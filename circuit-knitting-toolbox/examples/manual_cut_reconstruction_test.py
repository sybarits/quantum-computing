import unittest

import sys
import numpy as np
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit.result import ProbDistribution
import sys
sys.path.append("/home/symba/_dev/quantum-computing/circuit-knitting-toolbox/")
import json
from circuit_knitting_toolbox.circuit_cutting.wire_cutting import (
    cut_circuit_wires,
    evaluate_subcircuits,
    reconstruct_full_distribution,
    verify,
)
from qiskit_ibm_runtime import (
    QiskitRuntimeService,
    Options,
)


class TestReconstruction(unittest.TestCase):

    def setup(self):
        num_qubits = 5

        circuit = QuantumCircuit(num_qubits)
        for i in range(num_qubits):
            circuit.h(i)
        circuit.cx(0, 1)
        for i in range(2, num_qubits):
            circuit.t(i)
        circuit.cx(0, 2)
        circuit.rx(np.pi / 2, 4)
        circuit.rx(np.pi / 2, 0)
        circuit.rx(np.pi / 2, 1)
        circuit.cx(2, 4)
        circuit.t(0)
        circuit.t(1)
        circuit.cx(2, 3)
        circuit.ry(np.pi / 2, 4)
        for i in range(num_qubits):
            circuit.h(i)
        # circuit.draw("mpl", fold=-1, scale=0.7)
        print("\n\ncircuit\n\n")
        circuit.draw()

        cuts = cut_circuit_wires(
            circuit=circuit,
            method="manual",
            subcircuit_vertices=[[0,1],[2,3]]
            #max_subcircuit_width=5,
            #max_cuts=2,
            #num_subcircuits=[2],
        )
        print("\ncuts.keys()")
        print(cuts.keys())
        print("\n\n\nDRAW Subcircuits")
        # cuts["subcircuits"][0].draw("mpl", fold=-1, scale=0.6)
        cuts["subcircuits"][0].draw()
        cuts["subcircuits"][1].draw()

        options = Options(execution={"shots": 3})

        subcircuit_instance_probabilities = evaluate_subcircuits(cuts,service=None, backend_names=None, options=options)
        print("\nsubcircuit_instance_probabilities")
        print(subcircuit_instance_probabilities)
        
        reconstructed_probabilities = reconstruct_full_distribution(
            circuit, subcircuit_instance_probabilities, cuts
        )
        metrics, exact_probabilities = verify(circuit, reconstructed_probabilities)
        print("\nmetrics!")
        print(json.dumps(metrics, indent=4))

        # Create a dict for the reconstructed distribution
        reconstructed_distribution = {
            i: prob for i, prob in enumerate(reconstructed_probabilities)
        }

        print("\nreconstructed_distribution")
        print(json.dumps(reconstructed_distribution, indent=4))

        # Represent states as bitstrings (instead of ints)
        reconstructed_dict_bitstring = ProbDistribution(
            data=reconstructed_distribution
        ).binary_probabilities(num_bits=num_qubits)


        # Create the ground truth distribution dict
        exact_distribution = {i: prob for i, prob in enumerate(exact_probabilities)}
        

        # Represent states as bitstrings (instead of ints)
        exact_dict_bitstring = ProbDistribution(data=exact_distribution).binary_probabilities(
            num_bits=num_qubits
        )

        print("\nexact_dict_bitstring")
        print(json.dumps(exact_dict_bitstring, indent=4))
        

        # plot a histogram of the distributions
        plot_histogram(
            [exact_dict_bitstring, reconstructed_dict_bitstring],
            number_to_keep=8,
            figsize=(16, 6),
            sort="asc",
            legend=["Exact", "Reconstructed"],
        )


if __name__ == "__main__":
    t = TestReconstruction()
    t.setup()


