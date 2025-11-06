"""
Simple Example: RT-CSP and RT-CSP+ Comparison

This example demonstrates how to:
1. Generate a physical network
2. Generate slice requests
3. Run simulations with RT-CSP and RT-CSP+
4. Compare results
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simulation import (
    generate_physical_network,
    generate_slice_requests,
    SliceProvisioningSimulator
)


def main():
    print("=" * 70)
    print("5G Network Slice Provisioning: Simple Example")
    print("=" * 70)

    # Step 1: Generate Physical Network
    print("\n[Step 1] Generating physical network...")
    physical_network = generate_physical_network(
        num_nodes=50,  # Smaller network for quick demo
        topology_model="waxman",
        random_seed=42
    )
    print(f"  ✓ Created network with {physical_network.num_nodes()} nodes "
          f"and {physical_network.num_links()} links")

    # Step 2: Generate Slice Requests
    print("\n[Step 2] Generating slice requests...")
    slice_requests = generate_slice_requests(
        num_requests=500,  # Fewer requests for quick demo
        arrival_rate=0.04,
        avg_lifetime=500,
        random_seed=42
    )
    print(f"  ✓ Generated {len(slice_requests)} slice requests")
    print(f"  ✓ Simulation time span: 0 to {slice_requests[-1].arrival_time:.1f}")

    # Step 3: Run RT-CSP
    print("\n[Step 3] Running RT-CSP simulation...")
    simulator_rtcsp = SliceProvisioningSimulator(
        physical_network=physical_network.copy(),
        algorithm="RT-CSP",
        verbose=False
    )
    simulator_rtcsp.add_slice_requests(slice_requests)
    results_rtcsp = simulator_rtcsp.run()

    print(f"  ✓ RT-CSP completed")
    print(f"    - Acceptance Ratio: {results_rtcsp['metrics']['acceptance_ratio']:.2%}")
    print(f"    - Revenue/Cost Ratio: {results_rtcsp['metrics']['revenue_cost_ratio']:.3f}")

    # Step 4: Run RT-CSP+
    print("\n[Step 4] Running RT-CSP+ simulation...")
    simulator_rtcsp_plus = SliceProvisioningSimulator(
        physical_network=physical_network.copy(),
        algorithm="RT-CSP+",
        verbose=False
    )
    simulator_rtcsp_plus.add_slice_requests(slice_requests)
    results_rtcsp_plus = simulator_rtcsp_plus.run()

    print(f"  ✓ RT-CSP+ completed")
    print(f"    - Acceptance Ratio: {results_rtcsp_plus['metrics']['acceptance_ratio']:.2%}")
    print(f"    - Revenue/Cost Ratio: {results_rtcsp_plus['metrics']['revenue_cost_ratio']:.3f}")

    # Step 5: Compare Results
    print("\n[Step 5] Comparison Summary")
    print("=" * 70)

    print(f"\n{'Metric':<30} {'RT-CSP':<20} {'RT-CSP+':<20}")
    print("-" * 70)

    metrics_to_compare = [
        ('Acceptance Ratio', 'acceptance_ratio', '.2%'),
        ('Total Revenue', 'total_revenue', '.2f'),
        ('Total Cost', 'total_cost', '.2f'),
        ('Revenue/Cost Ratio', 'revenue_cost_ratio', '.3f'),
        ('Accepted Requests', 'accepted_requests', 'd'),
        ('Rejected Requests', 'rejected_requests', 'd')
    ]

    for metric_name, metric_key, fmt in metrics_to_compare:
        val_rtcsp = results_rtcsp['metrics'][metric_key]
        val_rtcsp_plus = results_rtcsp_plus['metrics'][metric_key]

        # Format values first, then apply alignment
        str_rtcsp = f"{val_rtcsp:{fmt}}"
        str_rtcsp_plus = f"{val_rtcsp_plus:{fmt}}"
        print(f"{metric_name:<30} {str_rtcsp:<20} {str_rtcsp_plus:<20}")

    # Calculate improvement
    print("\n" + "=" * 70)
    print("RT-CSP+ Improvements over RT-CSP:")
    print("-" * 70)

    acceptance_improvement = (
        (results_rtcsp_plus['metrics']['acceptance_ratio'] -
         results_rtcsp['metrics']['acceptance_ratio']) * 100
    )
    revenue_improvement = (
        (results_rtcsp_plus['metrics']['revenue_cost_ratio'] /
         results_rtcsp['metrics']['revenue_cost_ratio'] - 1) * 100
    )

    print(f"  Acceptance Ratio: +{acceptance_improvement:.2f} percentage points")
    print(f"  Revenue/Cost Ratio: +{revenue_improvement:.2f}%")

    print("\n" + "=" * 70)
    print("✓ Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
