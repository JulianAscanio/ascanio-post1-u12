"""Experimento 1: Preparación y medición del estado de Bell |Φ+⟩ en Qiskit."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram


def bell_state_experiment(shots: int = 1024) -> dict[str, int]:
    """Prepara el estado de Bell |Φ+> = (|00> + |11>)/√2, lo simula y guarda el histograma."""
    os.makedirs("capturas", exist_ok=True)

    # 2 qubits y 2 bits clásicos para almacenar la medición
    qc = QuantumCircuit(2, 2)

    # Paso 1: Hadamard en qubit 0 para crear superposición uniforme
    qc.h(0)
    # Paso 2: CNOT (control=0, target=1) para entrelazar ambos qubits
    qc.cx(0, 1)
    # Paso 3: Medición en la base computacional
    qc.measure([0, 1], [0, 1])

    # Transpilar y ejecutar en AerSimulator ideal
    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=shots)
    counts = job.result().get_counts()

    print(f"Resultados Bell |Φ+> ({shots} shots):")
    for state, count in sorted(counts.items()):
        pct = count / shots * 100
        print(f"  |{state}> : {count:4d} ({pct:.1f}%)")

    # Verificar correlación perfecta del entrelazamiento: nunca |01> ni |10>
    assert "01" not in counts and "10" not in counts, (
        "ERROR: aparecieron estados no entrelazados"
    )
    print("OK: correlación perfecta verificada")

    # Guardar histograma de medición
    fig = plot_histogram(counts, title="Estado de Bell |Φ+⟩ (1024 shots)")
    fig.savefig("capturas/bell_histogram.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"\nDiagrama del circuito:\n{qc.draw(output='text')}")
    return counts


if __name__ == "__main__":
    bell_state_experiment()
