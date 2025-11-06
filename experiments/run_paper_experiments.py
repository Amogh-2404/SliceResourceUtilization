"""
Paper Experiment Runner

Reproduces all experiments from the paper:
"Towards Efficiently Provisioning 5G Core Network Slice Based on
Resource and Topology Attributes" by Li et al. (2019)

Experiments:
1. Base case: 100 nodes, arrival_rate=0.04, link_prob=0.5
2. Varying link probability: 0.2, 0.5, 0.8
3. Varying arrival rate: 0.02, 0.04, 0.06, 0.08, 0.1
4. Varying network size: 50, 100, 150 nodes

Generates all 8 figures from the paper (Figures 2-9).
"""

import sys
import os
from pathlib import Path
import time
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simulation import (
    generate_physical_network,
    generate_slice_requests,
    SliceProvisioningSimulator
)
from src.visualization.static_plots import create_all_paper_figures


def run_single_experiment(
    num_nodes: int,
    num_requests: int,
    arrival_rate: float,
    connection_probability: float,
    algorithms: List[str],
    random_seed: int = 42,
    verbose: bool = False
) -> Dict[str, Dict]:
    """
    Run a single experiment configuration with multiple algorithms.

    Args:
        num_nodes: Number of physical nodes
        num_requests: Number of slice requests
        arrival_rate: Slice arrival rate
        connection_probability: Link connection probability for slice requests
        algorithms: List of algorithms to compare
        random_seed: Random seed for reproducibility
        verbose: Print simulation progress

    Returns:
        Dictionary mapping algorithm_name -> results
    """
    print(f"\n  Running experiment:")
    print(f"    Nodes: {num_nodes}, Requests: {num_requests}")
    print(f"    Arrival Rate: {arrival_rate}, Link Prob: {connection_probability}")

    # Generate physical network
    physical_network = generate_physical_network(
        num_nodes=num_nodes,
        topology_model="waxman",
        random_seed=random_seed
    )

    # Generate slice requests
    slice_requests = generate_slice_requests(
        num_requests=num_requests,
        arrival_rate=arrival_rate,
        connection_probability=connection_probability,
        random_seed=random_seed
    )

    results = {}

    for algorithm in algorithms:
        print(f"    Running {algorithm}...", end=" ", flush=True)
        start_time = time.time()

        # Create simulator
        simulator = SliceProvisioningSimulator(
            physical_network=physical_network.copy(),
            algorithm=algorithm,
            verbose=verbose
        )

        # Add requests and run
        simulator.add_slice_requests(slice_requests)
        result = simulator.run()
        results[algorithm] = result

        elapsed = time.time() - start_time
        acceptance = result['metrics']['acceptance_ratio']
        print(f"Done! (Acceptance: {acceptance:.2%}, Time: {elapsed:.1f}s)")

    return results


def run_base_case_experiment(
    algorithms: List[str] = ["RT-CSP", "RT-CSP+"],
    random_seed: int = 42
) -> Dict[str, Dict]:
    """
    Run base case experiment.

    Parameters from paper (Table 2):
    - Physical nodes: 100
    - Slice requests: 2000
    - Arrival rate: 0.04
    - Link probability: 0.5

    Args:
        algorithms: List of algorithms to compare
        random_seed: Random seed

    Returns:
        Results dictionary
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 1: Base Case")
    print("=" * 70)

    return run_single_experiment(
        num_nodes=100,
        num_requests=2000,
        arrival_rate=0.04,
        connection_probability=0.5,
        algorithms=algorithms,
        random_seed=random_seed
    )


def run_varying_link_probability_experiment(
    algorithms: List[str] = ["RT-CSP", "RT-CSP+"],
    random_seed: int = 42
) -> Dict[float, Dict[str, Dict]]:
    """
    Run experiment varying link connection probability.

    Parameters:
    - Link probabilities: 0.2, 0.5, 0.8
    - Fixed: 100 nodes, 2000 requests, arrival_rate=0.04

    Args:
        algorithms: List of algorithms to compare
        random_seed: Random seed

    Returns:
        Dictionary mapping link_prob -> {algorithm: results}
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: Varying Link Connection Probability")
    print("=" * 70)

    link_probabilities = [0.2, 0.5, 0.8]
    results = {}

    for prob in link_probabilities:
        print(f"\n--- Link Probability: {prob} ---")
        results[prob] = run_single_experiment(
            num_nodes=100,
            num_requests=2000,
            arrival_rate=0.04,
            connection_probability=prob,
            algorithms=algorithms,
            random_seed=random_seed
        )

    return results


def run_varying_arrival_rate_experiment(
    algorithms: List[str] = ["RT-CSP", "RT-CSP+"],
    random_seed: int = 42
) -> Dict[float, Dict[str, Dict]]:
    """
    Run experiment varying arrival rate.

    Parameters:
    - Arrival rates: 0.02, 0.04, 0.06, 0.08, 0.1
    - Fixed: 100 nodes, 2000 requests, link_prob=0.5

    Args:
        algorithms: List of algorithms to compare
        random_seed: Random seed

    Returns:
        Dictionary mapping arrival_rate -> {algorithm: results}
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Varying Arrival Rate")
    print("=" * 70)

    arrival_rates = [0.02, 0.04, 0.06, 0.08, 0.1]
    results = {}

    for rate in arrival_rates:
        print(f"\n--- Arrival Rate: {rate} ---")
        results[rate] = run_single_experiment(
            num_nodes=100,
            num_requests=2000,
            arrival_rate=rate,
            connection_probability=0.5,
            algorithms=algorithms,
            random_seed=random_seed
        )

    return results


def run_varying_network_size_experiment(
    algorithms: List[str] = ["RT-CSP", "RT-CSP+"],
    random_seed: int = 42
) -> Dict[int, Dict[str, Dict]]:
    """
    Run experiment varying network size.

    Parameters:
    - Network sizes: 50, 100, 150 nodes
    - Fixed: 2000 requests, arrival_rate=0.04, link_prob=0.5

    Args:
        algorithms: List of algorithms to compare
        random_seed: Random seed

    Returns:
        Dictionary mapping num_nodes -> {algorithm: results}
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: Varying Network Size")
    print("=" * 70)

    network_sizes = [50, 100, 150]
    results = {}

    for size in network_sizes:
        print(f"\n--- Network Size: {size} nodes ---")
        results[size] = run_single_experiment(
            num_nodes=size,
            num_requests=2000,
            arrival_rate=0.04,
            connection_probability=0.5,
            algorithms=algorithms,
            random_seed=random_seed
        )

    return results


def print_summary_table(results_dict: Dict[str, Dict]):
    """
    Print a summary table of results.

    Args:
        results_dict: Dictionary with algorithm names and their results
    """
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    algorithms = list(results_dict.keys())

    print(f"\n{'Metric':<35} {algorithms[0]:<15} {algorithms[1]:<15} {'Improvement':<15}")
    print("-" * 80)

    metrics = [
        ('Acceptance Ratio (%)', 'acceptance_ratio', lambda x: x * 100, '.2f'),
        ('Accepted Requests', 'accepted_requests', lambda x: x, 'd'),
        ('Rejected Requests', 'rejected_requests', lambda x: x, 'd'),
        ('Total Revenue', 'total_revenue', lambda x: x, '.2f'),
        ('Total Cost', 'total_cost', lambda x: x, '.2f'),
        ('Revenue/Cost Ratio', 'revenue_cost_ratio', lambda x: x, '.3f'),
    ]

    for metric_name, metric_key, transform, fmt in metrics:
        val1 = transform(results_dict[algorithms[0]]['metrics'][metric_key])
        val2 = transform(results_dict[algorithms[1]]['metrics'][metric_key])

        # Calculate improvement
        if metric_key in ['acceptance_ratio']:
            improvement = (val2 - val1)  # Percentage point difference
            improvement_str = f"+{improvement:{fmt}}pp"
        elif val1 > 0:
            improvement_pct = ((val2 / val1) - 1) * 100
            improvement_str = f"+{improvement_pct:.2f}%"
        else:
            improvement_str = "N/A"

        print(f"{metric_name:<35} {val1:{fmt}:<15} {val2:{fmt}:<15} {improvement_str:<15}")

    print("=" * 80)


def main():
    """Main experiment runner."""
    print("\n" + "=" * 70)
    print("5G CORE NETWORK SLICE PROVISIONING - PAPER EXPERIMENTS")
    print("Reproducing results from Li et al. (2019)")
    print("=" * 70)

    algorithms = ["RT-CSP", "RT-CSP+"]
    random_seed = 42
    output_dir = "output/figures"

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Track total time
    total_start = time.time()

    # Run all experiments
    print("\nRunning all experiments from the paper...")
    print("This may take several minutes...\n")

    # Experiment 1: Base case
    base_results = run_base_case_experiment(algorithms, random_seed)
    print_summary_table(base_results)

    # Experiment 2: Varying link probability
    link_prob_results = run_varying_link_probability_experiment(algorithms, random_seed)

    # Experiment 3: Varying arrival rate
    arrival_rate_results = run_varying_arrival_rate_experiment(algorithms, random_seed)

    # Experiment 4: Varying network size
    network_size_results = run_varying_network_size_experiment(algorithms, random_seed)

    total_time = time.time() - total_start

    # Generate all figures
    print("\n" + "=" * 70)
    print("GENERATING FIGURES")
    print("=" * 70)

    figures = create_all_paper_figures(
        base_results=base_results,
        link_prob_results=link_prob_results,
        arrival_rate_results=arrival_rate_results,
        network_size_results=network_size_results,
        output_dir=output_dir,
        show_plots=False
    )

    print("\n" + "=" * 70)
    print("ALL EXPERIMENTS COMPLETED!")
    print("=" * 70)
    print(f"\nTotal execution time: {total_time / 60:.1f} minutes")
    print(f"Generated {len(figures)} figures in: {output_dir}")
    print("\nFigures generated:")
    for i, fig_name in enumerate(sorted(figures.keys()), 1):
        print(f"  {i}. {fig_name}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
