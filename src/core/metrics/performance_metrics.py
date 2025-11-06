"""
Performance Metrics Module

Implements evaluation metrics for slice provisioning algorithms.
Based on Equations 7-11 from the paper.
"""

from typing import List, Dict, Tuple
from ..graph.slice_request import SliceRequest


class PerformanceMetrics:
    """
    Tracks and calculates performance metrics for slice provisioning simulation.

    Metrics:
        - Slice Acceptance Ratio (λ)
        - Long-term Average Provisioning Revenue (μ)
        - Provisioning Revenue-to-Cost Ratio (η)
    """

    def __init__(self):
        """Initialize metrics tracker."""
        self._total_requests = 0
        self._accepted_requests = 0
        self._rejected_requests = 0

        self._total_revenue = 0.0
        self._total_cost = 0.0

        # Time series data for plotting
        self._time_series = {
            'time': [],
            'acceptance_ratio': [],
            'cumulative_revenue': [],
            'cumulative_cost': [],
            'revenue_cost_ratio': []
        }

        # Per-time-window statistics
        self._window_stats = []

    def record_request(
        self,
        slice_request: SliceRequest,
        accepted: bool,
        physical_mapping: Dict = None
    ) -> None:
        """
        Record a slice request and its outcome.

        Args:
            slice_request: The slice request
            accepted: Whether the request was accepted
            physical_mapping: Physical mapping if accepted (for cost calculation)
        """
        self._total_requests += 1

        if accepted:
            self._accepted_requests += 1

            # Calculate revenue (Equation 8)
            revenue = slice_request.calculate_revenue()
            self._total_revenue += revenue

            # Calculate cost (Equation 10) if mapping provided
            if physical_mapping:
                cost = slice_request.calculate_cost(physical_mapping)
                self._total_cost += cost
        else:
            self._rejected_requests += 1

    def record_time_point(self, current_time: float) -> None:
        """
        Record metrics at a specific time point for time series analysis.

        Args:
            current_time: Current simulation time
        """
        self._time_series['time'].append(current_time)
        self._time_series['acceptance_ratio'].append(self.get_acceptance_ratio())
        self._time_series['cumulative_revenue'].append(self._total_revenue)
        self._time_series['cumulative_cost'].append(self._total_cost)
        self._time_series['revenue_cost_ratio'].append(self.get_revenue_cost_ratio())

    def get_acceptance_ratio(self) -> float:
        """
        Calculate the slice acceptance ratio.

        Equation 7:
            λ = lim(T→∞) ∑ Sₘ(t) / ∑ S(t)

        Returns:
            Acceptance ratio in [0, 1]
        """
        if self._total_requests == 0:
            return 0.0
        return self._accepted_requests / self._total_requests

    def get_rejection_ratio(self) -> float:
        """
        Calculate the slice rejection ratio.

        Returns:
            Rejection ratio in [0, 1]
        """
        if self._total_requests == 0:
            return 0.0
        return self._rejected_requests / self._total_requests

    def get_total_revenue(self) -> float:
        """
        Get the total provisioning revenue.

        Equation 8 (summed over all accepted slices):
            REV(G^S, t) = ∑ c(v^S) + ∑ b(e^S)

        Returns:
            Total revenue
        """
        return self._total_revenue

    def get_total_cost(self) -> float:
        """
        Get the total provisioning cost.

        Equation 10 (summed over all accepted slices):
            COST(G^S, t) = ∑ c(v^S) + ∑ |L(p^I(e^S))|·b(e^S)

        Returns:
            Total cost
        """
        return self._total_cost

    def get_average_revenue(self, simulation_time: float) -> float:
        """
        Calculate the long-term average provisioning revenue.

        Equation 9:
            μ = lim(T→∞) [∑ ∑ REV(G^S, t)] / T

        Args:
            simulation_time: Total simulation time

        Returns:
            Average revenue per time unit
        """
        if simulation_time <= 0:
            return 0.0
        return self._total_revenue / simulation_time

    def get_revenue_cost_ratio(self) -> float:
        """
        Calculate the provisioning revenue-to-cost ratio.

        Equation 11:
            η = REV / COST

        Returns:
            Revenue-to-cost ratio (higher is better)
        """
        if self._total_cost == 0:
            return 0.0
        return self._total_revenue / self._total_cost

    def get_time_series(self) -> Dict[str, List]:
        """
        Get time series data for plotting.

        Returns:
            Dictionary with time series arrays
        """
        return self._time_series.copy()

    def get_summary(self, simulation_time: float = None) -> Dict:
        """
        Get a summary of all metrics.

        Args:
            simulation_time: Total simulation time (for average revenue)

        Returns:
            Dictionary with all metrics
        """
        summary = {
            'total_requests': self._total_requests,
            'accepted_requests': self._accepted_requests,
            'rejected_requests': self._rejected_requests,
            'acceptance_ratio': self.get_acceptance_ratio(),
            'rejection_ratio': self.get_rejection_ratio(),
            'total_revenue': self._total_revenue,
            'total_cost': self._total_cost,
            'revenue_cost_ratio': self.get_revenue_cost_ratio()
        }

        if simulation_time is not None:
            summary['average_revenue'] = self.get_average_revenue(simulation_time)
            summary['simulation_time'] = simulation_time

        return summary

    def reset(self) -> None:
        """Reset all metrics to initial state."""
        self._total_requests = 0
        self._accepted_requests = 0
        self._rejected_requests = 0
        self._total_revenue = 0.0
        self._total_cost = 0.0
        self._time_series = {
            'time': [],
            'acceptance_ratio': [],
            'cumulative_revenue': [],
            'cumulative_cost': [],
            'revenue_cost_ratio': []
        }
        self._window_stats = []

    def __repr__(self) -> str:
        """String representation."""
        return (f"PerformanceMetrics(acceptance={self.get_acceptance_ratio():.2%}, "
                f"revenue={self._total_revenue:.2f}, "
                f"revenue/cost={self.get_revenue_cost_ratio():.3f})")


def calculate_slice_revenue(slice_request: SliceRequest) -> float:
    """
    Calculate the provisioning revenue of a slice request.

    Equation 8:
        REV(G^S, t) = ∑(v^S∈V^S) c(v^S) + ∑(e^S∈E^S) b(e^S)

    Args:
        slice_request: The slice request

    Returns:
        Revenue value
    """
    return slice_request.calculate_revenue()


def calculate_slice_cost(slice_request: SliceRequest, physical_mapping: Dict) -> float:
    """
    Calculate the provisioning cost of a slice request.

    Equation 10:
        COST(G^S, t) = ∑(v^S∈V^S) c(v^S) + ∑(e^S∈E^S) |L(p^I(e^S))|·b(e^S)

    Args:
        slice_request: The slice request
        physical_mapping: Physical mapping with 'nodes' and 'links'

    Returns:
        Cost value
    """
    return slice_request.calculate_cost(physical_mapping)


def compare_algorithm_performance(
    metrics_dict: Dict[str, PerformanceMetrics],
    simulation_time: float
) -> Dict[str, Dict]:
    """
    Compare performance of multiple algorithms.

    Args:
        metrics_dict: Dictionary mapping algorithm_name -> PerformanceMetrics
        simulation_time: Total simulation time

    Returns:
        Dictionary with comparison statistics
    """
    comparison = {}

    for algorithm_name, metrics in metrics_dict.items():
        comparison[algorithm_name] = metrics.get_summary(simulation_time)

    return comparison


def calculate_improvement_percentage(
    baseline_value: float,
    new_value: float
) -> float:
    """
    Calculate percentage improvement over baseline.

    Args:
        baseline_value: Baseline metric value
        new_value: New metric value

    Returns:
        Improvement percentage (positive means improvement)
    """
    if baseline_value == 0:
        return 0.0
    return ((new_value - baseline_value) / baseline_value) * 100
