"""Experimento 3: Algoritmo de Grover en 2 qubits para los 4 estados objetivo."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram


def build_grover_circuit(target: str = "11") -> QuantumCircuit:
    """Construye el circuito de Grover para n=2 qubits con 1 iteración (óptima para N=4)."""
    if target not in {"00", "01", "10", "11"}:
        raise ValueError(f"Estado objetivo inválido: {target}")

    qc = QuantumCircuit(2, 2)

    # Paso 1: Superposición uniforme sobre los 4 estados base
    qc.h([0, 1])
    qc.barrier()

    # Paso 2: Oráculo de fase — invierte la fase (-1) únicamente del estado target.
    # Nota: en Qiskit los bitstrings siguen orden little-endian (q1 q0),
    # donde target[0] corresponde a q1 y target[1] corresponde a q0.
    if target == "11":
        qc.cz(0, 1)
    elif target == "00":
        qc.x([0, 1])
        qc.cz(0, 1)
        qc.x([0, 1])
    elif target == "01":
        qc.x(1)
        qc.cz(0, 1)
        qc.x(1)
    elif target == "10":
        qc.x(0)
        qc.cz(0, 1)
        qc.x(0)
    qc.barrier()

    # Paso 3: Difusor (inversión alrededor de la media)
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    qc.barrier()

    # Medición
    qc.measure([0, 1], [0, 1])
    return qc


def grover_2qubits(target: str = "11", shots: int = 1024) -> dict[str, int]:
    """Ejecuta el algoritmo de Grover de 2 qubits buscando el estado target."""
    os.makedirs("capturas", exist_ok=True)
    qc = build_grover_circuit(target)

    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    counts = simulator.run(compiled_circuit, shots=shots).result().get_counts()

    print(f"Grover buscando |{target}> ({shots} shots):")
    for state, count in sorted(counts.items()):
        pct = count / shots * 100
        print(f"  |{state}>: {count:4d} ({pct:.1f}%)")

    top = max(counts, key=counts.get)
    status = "CORRECTO" if top == target else "ERROR"
    print(f"Estado más probable: |{top}> — {status}")
    assert top == target and counts[top] / shots > 0.90, (
        f"Grover no amplificó |{target}> por encima del 90%"
    )

    fig = plot_histogram(counts, title=f"Grover 2 qubits — Objetivo |{target}⟩")
    fig.savefig(f"capturas/grover_{target}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return counts


if __name__ == "__main__":
    for target_state in ["00", "01", "10", "11"]:
        grover_2qubits(target=target_state)
        print()
    print("Diagrama de referencia (target='11'):")
    print(build_grover_circuit("11").draw(output="text"))
