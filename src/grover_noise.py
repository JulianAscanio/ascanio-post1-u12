"""Experimento 4: Algoritmo de Grover bajo modelo de ruido despolarizante (NISQ)."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram


def build_grover_circuit(target: str = "11") -> QuantumCircuit:
    """Reconstruye el circuito de Grover (2 qubits) para el estado objetivo."""
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])

    # Oráculo de fase (convención little-endian de Qiskit: q1 q0)
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

    # Difusor (inversión alrededor de la media)
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])

    qc.measure([0, 1], [0, 1])
    return qc


def build_noise_model(p1q: float = 0.001, p2q: float = 0.01) -> NoiseModel:
    """Modelo de ruido despolarizante: p1q por puerta de 1 qubit (h, x),
    p2q por puerta de 2 qubits (cz) — órdenes de magnitud típicos de
    hardware NISQ superconductor publicados en la documentación de IBM Quantum."""
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1q, 1), ["h", "x"])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p2q, 2), ["cz"])
    return noise_model


def grover_noise_experiment(target: str = "11", shots: int = 1024) -> tuple[float, float]:
    """Compara la probabilidad de éxito de Grover sin ruido frente a NoiseModel."""
    os.makedirs("capturas", exist_ok=True)
    qc = build_grover_circuit(target)

    # Simulación ideal (sin ruido) — línea base
    ideal_sim = AerSimulator()
    qc_ideal = transpile(qc, ideal_sim)
    counts_ideal = ideal_sim.run(qc_ideal, shots=shots).result().get_counts()

    # Simulación con ruido despolarizante inyectado en cada puerta
    noisy_sim = AerSimulator(noise_model=build_noise_model())
    qc_noisy = transpile(qc, noisy_sim)
    counts_noisy = noisy_sim.run(qc_noisy, shots=shots).result().get_counts()

    p_ideal = counts_ideal.get(target, 0) / shots
    p_noisy = counts_noisy.get(target, 0) / shots

    print(f"Grover |{target}> sin ruido: {p_ideal * 100:.1f}% ({counts_ideal})")
    print(f"Grover |{target}> con ruido: {p_noisy * 100:.1f}% ({counts_noisy})")
    print(f"Degradación: {(p_ideal - p_noisy) * 100:.1f} puntos porcentuales")

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    plot_histogram(counts_ideal, ax=axs[0], title="Sin ruido (simulador ideal)")
    plot_histogram(counts_noisy, ax=axs[1], title="Con ruido (despolarizante)")
    fig.tight_layout()
    fig.savefig("capturas/grover_noise_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    return p_ideal, p_noisy


if __name__ == "__main__":
    grover_noise_experiment()
