"""Experimento 2: Algoritmo de Deutsch-Jozsa para n=2 qubits (oráculo constante vs balanceado)."""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def oracle_constante(n: int) -> QuantumCircuit:
    """Oráculo constante f(x)=0: no modifica el qubit ancilla."""
    return QuantumCircuit(n + 1, name="U_f(const)")


def oracle_balanceada(n: int) -> QuantumCircuit:
    """Oráculo balanceado f(x)=x_0 XOR x_1 ...: aplica CNOT de cada qubit al ancilla."""
    qc = QuantumCircuit(n + 1, name="U_f(bal)")
    for i in range(n):
        qc.cx(i, n)  # CNOT qubit_i -> ancilla
    return qc


def deutsch_jozsa(oracle_qc: QuantumCircuit, n: int, shots: int = 1024) -> tuple[dict[str, int], QuantumCircuit]:
    """Ejecuta el algoritmo de Deutsch-Jozsa con una única evaluación del oráculo."""
    qc = QuantumCircuit(n + 1, n)

    # Inicializar el ancilla en |-> = H|1> y los qubits de entrada en |+>
    qc.x(n)
    qc.h(range(n + 1))
    qc.barrier()

    # Única evaluación del oráculo cuántico (phase kickback)
    qc.compose(oracle_qc, inplace=True)
    qc.barrier()

    # Interferencia: Hadamard en los n qubits de entrada
    qc.h(range(n))

    # Medir únicamente los n qubits de entrada (el ancilla no se mide)
    qc.measure(range(n), range(n))

    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    counts = simulator.run(compiled_circuit, shots=shots).result().get_counts()
    return counts, qc


if __name__ == "__main__":
    n = 2

    # Oráculo constante: todos los resultados deben colapsar a "00"
    counts_c, qc_c = deutsch_jozsa(oracle_constante(n), n)
    print(f"Constante:  {counts_c}")

    # Oráculo balanceado: interferencia destructiva en "00", nunca debe aparecer "00"
    counts_b, qc_b = deutsch_jozsa(oracle_balanceada(n), n)
    print(f"Balanceada: {counts_b}")

    assert "00" in counts_c and len(counts_c) == 1, "Error: oráculo constante no retornó únicamente 00"
    assert "00" not in counts_b, "Error: oráculo balanceado retornó 00"
    print("OK: Deutsch-Jozsa verifica correctamente ambos oráculos en 1 evaluación")

    print(f"\nCircuito (oráculo constante):\n{qc_c.draw(output='text')}")
    print(f"\nCircuito (oráculo balanceado):\n{qc_b.draw(output='text')}")
