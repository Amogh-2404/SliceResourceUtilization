"""
Main Simulator Module

Implements discrete event simulation for slice provisioning.
Manages slice arrivals, departures, and performance tracking.
"""

import heapq
from typing import List, Dict, Optional, Tuple
from enum import Enum
from ..core.graph.physical_network import PhysicalNetwork
from ..core.graph.slice_request import SliceRequest
from ..core.algorithms.rt_csp import RTCSP, RTCSPPlus, ProvisioningResult
from ..core.metrics.performance_metrics import PerformanceMetrics
from .topology_generator import generate_physical_network
from .request_generator import generate_slice_requests


class EventType(Enum):
    """Types of events in the simulation."""
    ARRIVAL = "arrival"
    DEPARTURE = "departure"


class Event:
    """Represents a simulation event."""

    def __init__(self, time: float, event_type: EventType, slice_request: SliceRequest):
        """
        Initialize an event.

        Args:
            time: Event time
            event_type: Type of event (arrival or departure)
            slice_request: Associated slice request
        """
        self.time = time
        self.event_type = event_type
        self.slice_request = slice_request

    def __lt__(self, other: 'Event') -> bool:
        """Compare events by time (for priority queue)."""
        return self.time < other.time

    def __repr__(self) -> str:
        """String representation."""
        return (f"Event(time={self.time:.2f}, type={self.event_type.value}, "
                f"slice={self.slice_request.slice_id})")


class SliceProvisioningSimulator:
    """
    Discrete event simulator for 5G core network slice provisioning.

    Simulates:
        - Slice request arrivals (Poisson process)
        - Slice provisioning using RT-CSP or RT-CSP+
        - Slice departures (after lifetime expires)
        - Performance metric tracking
    """

    def __init__(
        self,
        physical_network: PhysicalNetwork,
        algorithm: str = "RT-CSP+",
        alpha: float = 0.5,
        beta: float = 0.5,
        k: int = 3,
        verbose: bool = False
    ):
        """
        Initialize the simulator.

        Args:
            physical_network: Physical network topology
            algorithm: "RT-CSP" or "RT-CSP+"
            alpha: Weight for local attributes
            beta: Weight for global attributes
            k: Number of shortest paths
            verbose: Print simulation progress
        """
        self.physical_network = physical_network
        self.algorithm_name = algorithm
        self.verbose = verbose

        # Initialize provisioning algorithm
        if algorithm.upper() == "RT-CSP+":
            self.algorithm = RTCSPPlus(alpha=alpha, beta=beta, k=k)
        else:
            self.algorithm = RTCSP(alpha=alpha, beta=beta, k=k)

        # Event queue (priority queue)
        self.event_queue: List[Event] = []

        # Active slices: slice_id -> (SliceRequest, ProvisioningResult)
        self.active_slices: Dict[str, Tuple[SliceRequest, ProvisioningResult]] = {}

        # Performance metrics
        self.metrics = PerformanceMetrics()

        # Current simulation time
        self.current_time = 0.0

        # Statistics
        self.total_arrivals = 0
        self.total_departures = 0

    def add_slice_requests(self, slice_requests: List[SliceRequest]) -> None:
        """
        Add slice requests to the event queue.

        Args:
            slice_requests: List of slice requests
        """
        for slice_request in slice_requests:
            # Add arrival event
            arrival_event = Event(
                slice_request.arrival_time,
                EventType.ARRIVAL,
                slice_request
            )
            heapq.heappush(self.event_queue, arrival_event)

    def run(self, max_time: Optional[float] = None) -> Dict:
        """
        Run the simulation until all events are processed.

        Args:
            max_time: Maximum simulation time (None for unlimited)

        Returns:
            Dictionary with simulation results and metrics
        """
        if self.verbose:
            print(f"Starting simulation with {self.algorithm_name}")
            print(f"Physical network: {self.physical_network.num_nodes()} nodes, "
                  f"{self.physical_network.num_links()} links")
            print(f"Total requests: {len(self.event_queue)}")
            print("-" * 60)

        event_count = 0
        last_log_time = 0.0
        log_interval = 1000  # Log every 1000 time units

        while self.event_queue:
            # Get next event
            event = heapq.heappop(self.event_queue)

            # Check max time
            if max_time is not None and event.time > max_time:
                break

            # Update current time
            self.current_time = event.time

            # Process event
            if event.event_type == EventType.ARRIVAL:
                self._process_arrival(event.slice_request)
            elif event.event_type == EventType.DEPARTURE:
                self._process_departure(event.slice_request)

            event_count += 1

            # Periodic logging
            if self.verbose and self.current_time - last_log_time >= log_interval:
                self._log_progress()
                last_log_time = self.current_time

            # Record metrics periodically
            if event_count % 100 == 0:
                self.metrics.record_time_point(self.current_time)

        # Final metrics recording
        self.metrics.record_time_point(self.current_time)

        if self.verbose:
            print("\n" + "=" * 60)
            print("Simulation completed")
            self._print_summary()

        return self._get_results()

    def _process_arrival(self, slice_request: SliceRequest) -> None:
        """
        Process a slice arrival event.

        Args:
            slice_request: Arriving slice request
        """
        self.total_arrivals += 1

        if self.verbose and self.total_arrivals % 100 == 0:
            print(f"[{self.current_time:.1f}] Processing arrival #{self.total_arrivals}: "
                  f"{slice_request.slice_id}")

        # Attempt provisioning
        result = self.algorithm.provision_slice(slice_request, self.physical_network)

        if result.success:
            # Provisioning succeeded
            slice_request.set_status("active")

            # Store active slice
            self.active_slices[slice_request.slice_id] = (slice_request, result)

            # Schedule departure event
            departure_event = Event(
                slice_request.departure_time,
                EventType.DEPARTURE,
                slice_request
            )
            heapq.heappush(self.event_queue, departure_event)

            # Record metrics
            physical_mapping = {
                'nodes': result.node_mapping,
                'links': result.link_mapping
            }
            self.metrics.record_request(slice_request, accepted=True, physical_mapping=physical_mapping)

        else:
            # Provisioning failed
            slice_request.set_status("rejected")

            # Record metrics
            self.metrics.record_request(slice_request, accepted=False)

            if self.verbose and self.total_arrivals <= 10:
                print(f"  -> REJECTED: {result.failure_reason}")

    def _process_departure(self, slice_request: SliceRequest) -> None:
        """
        Process a slice departure event.

        Args:
            slice_request: Departing slice request
        """
        self.total_departures += 1

        if slice_request.slice_id not in self.active_slices:
            # Slice was never accepted or already departed
            return

        if self.verbose and self.total_departures % 100 == 0:
            print(f"[{self.current_time:.1f}] Processing departure #{self.total_departures}: "
                  f"{slice_request.slice_id}")

        # Release resources
        self.physical_network.deallocate_slice(slice_request.slice_id)

        # Update status
        slice_request.set_status("completed")

        # Remove from active slices
        del self.active_slices[slice_request.slice_id]

    def _log_progress(self) -> None:
        """Log simulation progress."""
        util = self.physical_network.get_resource_utilization()
        print(f"[{self.current_time:.1f}] "
              f"Arrivals: {self.total_arrivals}, "
              f"Active: {len(self.active_slices)}, "
              f"Acceptance: {self.metrics.get_acceptance_ratio():.2%}, "
              f"CPU Util: {util['cpu_utilization_percent']:.1f}%, "
              f"BW Util: {util['bandwidth_utilization_percent']:.1f}%")

    def _print_summary(self) -> None:
        """Print simulation summary."""
        summary = self.metrics.get_summary(self.current_time)

        print("\nSimulation Summary:")
        print(f"  Total simulation time: {self.current_time:.2f}")
        print(f"  Total arrivals: {self.total_arrivals}")
        print(f"  Total departures: {self.total_departures}")
        print(f"  Accepted requests: {summary['accepted_requests']}")
        print(f"  Rejected requests: {summary['rejected_requests']}")
        print(f"  Acceptance ratio: {summary['acceptance_ratio']:.2%}")
        print(f"  Total revenue: {summary['total_revenue']:.2f}")
        print(f"  Total cost: {summary['total_cost']:.2f}")
        print(f"  Revenue/Cost ratio: {summary['revenue_cost_ratio']:.3f}")
        if 'average_revenue' in summary:
            print(f"  Average revenue: {summary['average_revenue']:.3f}")

        util = self.physical_network.get_resource_utilization()
        print(f"\nFinal Resource Utilization:")
        print(f"  CPU: {util['cpu_utilization_percent']:.2f}%")
        print(f"  Bandwidth: {util['bandwidth_utilization_percent']:.2f}%")

    def _get_results(self) -> Dict:
        """
        Get simulation results.

        Returns:
            Dictionary with results and metrics
        """
        summary = self.metrics.get_summary(self.current_time)
        time_series = self.metrics.get_time_series()
        util = self.physical_network.get_resource_utilization()

        return {
            'algorithm': self.algorithm_name,
            'simulation_time': self.current_time,
            'total_arrivals': self.total_arrivals,
            'total_departures': self.total_departures,
            'metrics': summary,
            'time_series': time_series,
            'final_utilization': util,
            'physical_network_stats': {
                'num_nodes': self.physical_network.num_nodes(),
                'num_links': self.physical_network.num_links()
            }
        }

    def get_metrics(self) -> PerformanceMetrics:
        """Get the metrics tracker."""
        return self.metrics

    def reset(self) -> None:
        """Reset the simulator to initial state."""
        self.event_queue.clear()
        self.active_slices.clear()
        self.metrics.reset()
        self.physical_network.reset_resources()
        self.current_time = 0.0
        self.total_arrivals = 0
        self.total_departures = 0


# Utility functions

def run_single_simulation(
    num_substrate_nodes: int = 100,
    num_requests: int = 2000,
    arrival_rate: float = 0.04,
    algorithm: str = "RT-CSP+",
    verbose: bool = False,
    random_seed: Optional[int] = None,
    **kwargs
) -> Dict:
    """
    Run a single simulation with default parameters.

    Args:
        num_substrate_nodes: Number of physical nodes
        num_requests: Number of slice requests
        arrival_rate: Slice arrival rate
        algorithm: "RT-CSP" or "RT-CSP+"
        verbose: Print progress
        random_seed: Random seed for reproducibility
        **kwargs: Additional parameters

    Returns:
        Simulation results dictionary
    """
    # Generate physical network
    physical_network = generate_physical_network(
        num_nodes=num_substrate_nodes,
        topology_model="waxman",
        random_seed=random_seed
    )

    # Generate slice requests
    slice_requests = generate_slice_requests(
        num_requests=num_requests,
        arrival_rate=arrival_rate,
        random_seed=random_seed,
        **kwargs
    )

    # Create simulator
    simulator = SliceProvisioningSimulator(
        physical_network=physical_network,
        algorithm=algorithm,
        verbose=verbose
    )

    # Add requests and run
    simulator.add_slice_requests(slice_requests)
    results = simulator.run()

    return results


def run_comparison(
    algorithms: List[str] = ["RT-CSP", "RT-CSP+"],
    **kwargs
) -> Dict[str, Dict]:
    """
    Run simulation comparing multiple algorithms.

    Args:
        algorithms: List of algorithm names
        **kwargs: Parameters for simulation

    Returns:
        Dictionary mapping algorithm_name -> results
    """
    comparison_results = {}

    for algorithm in algorithms:
        print(f"\nRunning {algorithm}...")
        results = run_single_simulation(algorithm=algorithm, **kwargs)
        comparison_results[algorithm] = results

    return comparison_results


def main():
    """Main function for command-line execution."""
    import argparse

    parser = argparse.ArgumentParser(description="5G Network Slice Provisioning Simulator")
    parser.add_argument("--nodes", type=int, default=100, help="Number of physical nodes")
    parser.add_argument("--requests", type=int, default=2000, help="Number of slice requests")
    parser.add_argument("--arrival-rate", type=float, default=0.04, help="Slice arrival rate")
    parser.add_argument("--algorithm", type=str, default="RT-CSP+", choices=["RT-CSP", "RT-CSP+"])
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--verbose", action="store_true", help="Print progress")

    args = parser.parse_args()

    results = run_single_simulation(
        num_substrate_nodes=args.nodes,
        num_requests=args.requests,
        arrival_rate=args.arrival_rate,
        algorithm=args.algorithm,
        verbose=args.verbose,
        random_seed=args.seed
    )

    print("\nFinal Results:")
    print(f"Acceptance Ratio: {results['metrics']['acceptance_ratio']:.2%}")
    print(f"Revenue/Cost Ratio: {results['metrics']['revenue_cost_ratio']:.3f}")


if __name__ == "__main__":
    main()
