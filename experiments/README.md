# Experiments

This directory contains scripts to reproduce all experiments from the paper.

## Paper Experiments

### Overview

The paper presents four main experiments:

1. **Base Case**: 100 nodes, 2000 requests, arrival rate 0.04, link probability 0.5
2. **Varying Link Probability**: Tests with link probabilities 0.2, 0.5, 0.8
3. **Varying Arrival Rate**: Tests with arrival rates 0.02, 0.04, 0.06, 0.08, 0.1
4. **Varying Network Size**: Tests with 50, 100, 150 physical nodes

### Running All Experiments

To reproduce all 8 figures from the paper:

```bash
python experiments/run_paper_experiments.py
```

This will:
- Run all four experiment configurations
- Compare RT-CSP and RT-CSP+ algorithms
- Generate all 8 figures (Figures 2-9 from the paper)
- Save results to `output/figures/`

**Note**: This may take 10-30 minutes depending on your machine.

### Generated Figures

The script generates the following figures:

- **Figure 2**: Acceptance ratio over time
- **Figure 3a**: Long-term average revenue comparison
- **Figure 3b**: Revenue-to-cost ratio comparison
- **Figure 4**: Acceptance ratio vs link connection probability
- **Figure 5**: Revenue-cost ratio vs link connection probability
- **Figure 6**: Acceptance ratio vs arrival rate
- **Figure 7**: Revenue-cost ratio vs arrival rate
- **Figure 8**: Acceptance ratio vs network size
- **Figure 9**: Revenue-cost ratio vs network size

### Output

All figures are saved in `output/figures/` as high-resolution PNG files (300 DPI).

The script also prints summary tables comparing RT-CSP and RT-CSP+ performance across all metrics.

## Custom Experiments

You can create custom experiments by using the simulation API directly:

```python
from src.simulation import (
    generate_physical_network,
    generate_slice_requests,
    SliceProvisioningSimulator
)

# Generate network and requests
physical_network = generate_physical_network(num_nodes=100)
slice_requests = generate_slice_requests(num_requests=1000)

# Run simulation
simulator = SliceProvisioningSimulator(
    physical_network=physical_network,
    algorithm="RT-CSP+"
)
simulator.add_slice_requests(slice_requests)
results = simulator.run()

# Access results
print(f"Acceptance ratio: {results['metrics']['acceptance_ratio']:.2%}")
```

## Expected Results

Based on the paper, you should expect:

- **RT-CSP+** outperforms **RT-CSP** in:
  - Acceptance ratio (typically 5-15% improvement)
  - Revenue-to-cost ratio (typically 10-20% improvement)

- Performance trends:
  - Higher link probability ’ higher acceptance ratio
  - Higher arrival rate ’ lower acceptance ratio (more congestion)
  - Larger network size ’ higher acceptance ratio (more resources)
