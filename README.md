# 5G Network Slice Provisioning: RT-CSP & RT-CSP+

Implementation of "Towards Efficiently Provisioning 5G Core Network Slice Based on Resource and Topology Attributes" by Li et al. (2019).

## Overview

This project implements the RT-CSP and RT-CSP+ algorithms for efficient provisioning of 5G core network slices by jointly considering:
- **Resource attributes**: Local and global network resources (CPU, bandwidth)
- **Topology attributes**: Degree centrality and closeness centrality

### Key Algorithms

- **RT-CSP**: Two-stage heuristic slice provisioning with k-shortest path based link provisioning
- **RT-CSP+**: Enhanced version with minMaxBWUtilHops strategy to minimize bottlenecks

## Features

✨ **Complete Implementation**
- Node ranking based on 4 attributes (LR, GR, DC, CC)
- Cooperative provisioning coefficient for node selection
- K-shortest path algorithm with bandwidth constraints
- minMaxBWUtilHops strategy for optimal path selection

📊 **Comprehensive Simulation**
- Discrete event simulator
- Waxman topology generation
- Poisson arrival process
- Exponential lifetime distribution
- Configurable parameters matching the paper

📈 **Visualization & Analysis**
- Replication of all 8 figures from the paper (Matplotlib)
- Network topology visualization (NetworkX)
- Slice-to-physical mapping visualization
- Resource utilization heatmaps (CPU & Bandwidth)
- Time series plots (acceptance ratio, revenue, cost)
- Interactive Dash dashboard with real-time controls

📚 **Technical Documentation**
- Complete mathematical formulations (20 equations)
- Symbol glossary (Table 1)
- Algorithm explanations
- API reference
- User guide

## Installation

```bash
# Clone the repository
git clone https://github.com/Amogh-2404/SliceResourceUtilization
cd SliceResourceUtilization

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

```python
from src.core.algorithms.rt_csp_plus import RTCSPPlus
from src.simulation.simulator import SliceProvisioningSimulator

# Initialize simulator
config = {
    'substrate_nodes': 100,
    'algorithm': 'RT-CSP+',
    'num_requests': 2000,
    'arrival_rate': 0.04
}

simulator = SliceProvisioningSimulator(config)
simulator.setup()

# Run simulation
results = simulator.run()

# Analyze results
print(f"Acceptance Ratio: {results['acceptance_ratio']:.2%}")
print(f"Average Revenue: {results['avg_revenue']:.2f}")
print(f"Revenue/Cost Ratio: {results['revenue_cost_ratio']:.3f}")
```

## Repository Structure

```
SliceResourceUtilization/
├── src/
│   ├── core/                  # Core algorithms and data structures
│   │   ├── graph/            # Network graph classes
│   │   ├── algorithms/       # Provisioning algorithms
│   │   ├── metrics/          # Resource and topology attributes
│   │   └── pathfinding/      # K-shortest path
│   ├── simulation/           # Simulation engine
│   ├── visualization/        # Plots and dashboards
│   └── utils/                # Configuration and helpers
├── tests/                    # Test suite
├── docs/                     # Documentation
├── config/                   # Configuration files
├── results/                  # Generated results
└── notebooks/                # Jupyter notebooks
```

## Running Experiments

### Quick Start Example

```bash
# Run a simple comparison between RT-CSP and RT-CSP+
python3 examples/simple_example.py
```

### Reproduce All Paper Results

```bash
# Run all experiments from the paper (generates Figures 2-9)
# Note: This may take 10-30 minutes
python3 experiments/run_paper_experiments.py
```

This will:
- Run base case experiment (100 nodes, 2000 requests)
- Test varying link probabilities (0.2, 0.5, 0.8)
- Test varying arrival rates (0.02-0.1)
- Test varying network sizes (50, 100, 150 nodes)
- Generate all 8 figures and save to `output/figures/`

### Network Visualization

```bash
# Visualize network topology and slice mappings
python3 examples/visualize_mapping.py
```

This demonstrates:
- Physical network visualization
- Slice request topology
- Slice-to-physical mapping
- Resource utilization heatmaps

### Launch Interactive Dashboard

```bash
# Start the web dashboard
python3 run_dashboard.py

# Or with custom host/port
python3 run_dashboard.py --host 0.0.0.0 --port 8080

# Then open your browser to http://localhost:8050
```

Features:
- Real-time simulation control and visualization
- Interactive parameter tuning (network size, arrival rate, etc.)
- Multiple visualization tabs (acceptance ratio, revenue, utilization)
- Algorithm comparison (RT-CSP vs RT-CSP+)
- Detailed performance metrics

See `src/visualization/dashboard/README.md` for complete documentation.

### Custom Simulations

```bash
# Run with custom parameters
python -m src.simulation.simulator \
    --nodes 150 \
    --arrival-rate 0.06 \
    --algorithm RT-CSP+
```

## Configuration

Edit `config/simulation_params.yaml` to customize:
- Physical network topology (nodes, connectivity, resources)
- Slice request parameters (size, demands, arrival rate)
- Algorithm parameters (α, β, k, ε)

## Performance Metrics

The implementation tracks three key metrics from the paper:

1. **Slice Acceptance Ratio (λ)**: Ratio of accepted to total requests
2. **Long-term Average Revenue (μ)**: Revenue from provisioned slices
3. **Revenue-to-Cost Ratio (η)**: Efficiency of resource utilization

## Mathematical Formulations

All 20 equations from the paper are implemented:

- **Node Ranking**: Equations 12-19 (LR, GR, DC, CC, combined scoring)
- **Constraints**: Equations 1-6 (CPU, bandwidth, location, one-to-one mapping)
- **Link Selection**: Equation 20 (minMaxBWUtilHops strategy)
- **Performance Metrics**: Equations 7-11 (acceptance, revenue, cost)

See [docs/mathematical_formulations.md](docs/mathematical_formulations.md) for complete details.

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

## Documentation

- [Mathematical Formulations](docs/mathematical_formulations.md) - All equations with explanations
- [Symbols Glossary](docs/symbols_glossary.md) - Notation from Table 1
- [Algorithm Guide](docs/algorithms_explained.md) - Step-by-step walkthroughs
- [API Reference](docs/api_reference.md) - Class and method documentation
- [User Guide](docs/user_guide.md) - Examples and tutorials

## Citation

If you use this code in your research, please cite the original paper:

```bibtex
@article{li2019towards,
  title={Towards Efficiently Provisioning 5G Core Network Slice Based on Resource and Topology Attributes},
  author={Li, Xin and Guo, Chengcheng and Xu, Jun and Gupta, Lav and Jain, Raj},
  journal={Applied Sciences},
  volume={9},
  number={20},
  pages={4361},
  year={2019},
  publisher={MDPI}
}
```

## License

MIT License

## Authors

- Original Paper: Li et al. (2019)
- Implementation: R.Amogh

## Acknowledgments

This implementation is based on the research paper published in Applied Sciences (2019). We thank the original authors for their comprehensive work on 5G network slice provisioning.
