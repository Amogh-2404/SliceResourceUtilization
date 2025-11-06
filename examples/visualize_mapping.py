"""
Network Visualization Example

Demonstrates how to visualize:
1. Physical network topology
2. Slice request topology
3. Slice-to-physical mapping
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
from src.visualization.network_viz import (
    visualize_physical_network,
    visualize_slice_request,
    visualize_slice_mapping,
    visualize_network_utilization_heatmap
)


def main():
    print("=" * 70)
    print("Network Visualization Example")
    print("=" * 70)

    # Step 1: Generate Physical Network
    print("\n[Step 1] Generating physical network...")
    physical_network = generate_physical_network(
        num_nodes=20,  # Small network for clear visualization
        topology_model="waxman",
        random_seed=42
    )
    print(f"   Created network with {physical_network.num_nodes()} nodes")

    # Visualize physical network (initial state)
    print("\n[Step 2] Visualizing initial physical network...")
    visualize_physical_network(
        physical_network,
        layout_type='positions',
        title="Physical Network (Initial State)",
        output_path="output/figures/physical_network_initial.png",
        show_plot=False
    )

    # Step 2: Generate Slice Requests
    print("\n[Step 3] Generating slice requests...")
    slice_requests = generate_slice_requests(
        num_requests=5,
        arrival_rate=0.1,
        node_range=(3, 6),  # Smaller slices
        connection_probability=0.6,
        random_seed=42
    )
    print(f"   Generated {len(slice_requests)} slice requests")

    # Visualize first slice request
    print("\n[Step 4] Visualizing first slice request...")
    first_slice = slice_requests[0]
    visualize_slice_request(
        first_slice,
        title=f"Slice Request: {first_slice.slice_id}",
        output_path="output/figures/slice_request_example.png",
        show_plot=False
    )

    # Step 3: Provision slice using RT-CSP+
    print("\n[Step 5] Provisioning slice using RT-CSP+...")
    simulator = SliceProvisioningSimulator(
        physical_network=physical_network,
        algorithm="RT-CSP+",
        verbose=False
    )

    # Provision just the first slice
    from src.core.algorithms.rt_csp import RTCSPPlus
    algorithm = RTCSPPlus()
    result = algorithm.provision_slice(first_slice, physical_network)

    if result.success:
        print(f"   Slice {first_slice.slice_id} provisioned successfully!")

        # Visualize the mapping
        print("\n[Step 6] Visualizing slice mapping...")
        visualize_slice_mapping(
            physical_network=physical_network,
            slice_request=first_slice,
            node_mapping=result.node_mapping,
            link_mapping=result.link_mapping,
            title=f"Slice Mapping: {first_slice.slice_id}",
            output_path="output/figures/slice_mapping_example.png",
            show_plot=False
        )

        # Visualize resource utilization
        print("\n[Step 7] Visualizing resource utilization...")

        # CPU utilization heatmap
        visualize_network_utilization_heatmap(
            physical_network,
            resource_type='cpu',
            title="CPU Utilization After Provisioning",
            output_path="output/figures/cpu_utilization_heatmap.png",
            show_plot=False
        )

        # Bandwidth utilization heatmap
        visualize_network_utilization_heatmap(
            physical_network,
            resource_type='bandwidth',
            title="Bandwidth Utilization After Provisioning",
            output_path="output/figures/bandwidth_utilization_heatmap.png",
            show_plot=False
        )

    else:
        print(f"   Slice {first_slice.slice_id} rejected: {result.failure_reason}")

    # Step 4: Provision multiple slices and visualize
    print("\n[Step 8] Provisioning multiple slices...")
    simulator = SliceProvisioningSimulator(
        physical_network=physical_network.copy(),
        algorithm="RT-CSP+",
        verbose=False
    )
    simulator.add_slice_requests(slice_requests)
    results = simulator.run()

    print(f"   Simulation completed")
    print(f"    - Accepted: {results['metrics']['accepted_requests']}")
    print(f"    - Rejected: {results['metrics']['rejected_requests']}")
    print(f"    - Acceptance Ratio: {results['metrics']['acceptance_ratio']:.2%}")

    # Visualize final state
    print("\n[Step 9] Visualizing physical network after multiple slices...")
    visualize_physical_network(
        simulator.physical_network,
        layout_type='positions',
        title="Physical Network (After Multiple Slices)",
        output_path="output/figures/physical_network_final.png",
        show_plot=False
    )

    # Final heatmaps
    print("\n[Step 10] Visualizing final resource utilization...")
    visualize_network_utilization_heatmap(
        simulator.physical_network,
        resource_type='cpu',
        title="Final CPU Utilization",
        output_path="output/figures/final_cpu_utilization.png",
        show_plot=False
    )

    visualize_network_utilization_heatmap(
        simulator.physical_network,
        resource_type='bandwidth',
        title="Final Bandwidth Utilization",
        output_path="output/figures/final_bandwidth_utilization.png",
        show_plot=False
    )

    print("\n" + "=" * 70)
    print("Visualization Example Completed!")
    print("=" * 70)
    print("\nGenerated visualizations:")
    print("  1. physical_network_initial.png - Initial physical network")
    print("  2. slice_request_example.png - Example slice request")
    print("  3. slice_mapping_example.png - Slice-to-physical mapping")
    print("  4. cpu_utilization_heatmap.png - CPU utilization after first slice")
    print("  5. bandwidth_utilization_heatmap.png - BW utilization after first slice")
    print("  6. physical_network_final.png - Physical network after all slices")
    print("  7. final_cpu_utilization.png - Final CPU utilization")
    print("  8. final_bandwidth_utilization.png - Final BW utilization")
    print("\nAll figures saved to: output/figures/")
    print("=" * 70)


if __name__ == "__main__":
    main()
