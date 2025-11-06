# Interactive Dashboard

Web-based interactive dashboard for 5G Network Slice Provisioning simulation and visualization.

## Features

### Real-time Simulation
- Configure and run simulations directly from the browser
- Adjust parameters on-the-fly
- Visualize results in real-time

### Interactive Controls
- **Algorithm Selection**: Choose between RT-CSP and RT-CSP+
- **Topology Model**: Select Waxman, ErdQs-Rényi, or Barabási-Albert
- **Network Size**: Adjust number of physical nodes (20-200)
- **Request Volume**: Configure number of slice requests (100-2000)
- **Arrival Rate**: Control request arrival rate (0.02-0.1)
- **Link Probability**: Adjust slice link connection probability (0.2-0.8)

### Visualization Tabs

#### 1. Acceptance Ratio
- Time series plot showing acceptance ratio evolution
- Interactive hover for detailed values
- Smooth line with markers

#### 2. Revenue
- Bar chart comparing total revenue and cost
- Clear visual comparison
- Exact values displayed

#### 3. Resource Utilization
- CPU and bandwidth utilization percentages
- Color-coded bars for easy interpretation
- Final state after simulation completion

#### 4. Network Topology
- Network statistics visualization
- Node and link counts
- Average degree calculation

#### 5. Detailed Stats
- Comprehensive table of all metrics
- Simulation parameters
- Performance metrics
- Resource utilization details

## Quick Start

### Option 1: Using the launcher script

```bash
# From project root
python3 run_dashboard.py

# With custom host/port
python3 run_dashboard.py --host 0.0.0.0 --port 8080

# With debug mode
python3 run_dashboard.py --debug
```

### Option 2: Direct import

```python
from src.visualization.dashboard import run_dashboard

run_dashboard(host='127.0.0.1', port=8050, debug=True)
```

### Option 3: As a module

```bash
python3 -m src.visualization.dashboard.app
```

## Using the Dashboard

### Step 1: Configure Parameters
1. Select your algorithm (RT-CSP or RT-CSP+)
2. Choose topology model
3. Adjust sliders for:
   - Number of physical nodes
   - Number of slice requests
   - Arrival rate
   - Link probability

### Step 2: Run Simulation
1. Click the "Run Simulation" button
2. Wait for completion (status will appear below controls)
3. View results in the tabs

### Step 3: Analyze Results
- Switch between tabs to view different metrics
- Hover over plots for detailed values
- Check detailed stats for comprehensive information

### Step 4: Compare Configurations
1. Note the results from your current run
2. Adjust parameters
3. Run again
4. Compare with previous results

### Step 5: Reset
- Click "Reset" button to clear results
- Configure new parameters
- Run fresh simulation

## Tips for Best Results

### Performance Testing
- Start with smaller networks (20-50 nodes) for quick tests
- Use larger networks (100-200 nodes) for comprehensive analysis
- Balance request volume with network size

### Algorithm Comparison
1. Run RT-CSP with specific parameters
2. Note the acceptance ratio and revenue/cost
3. Reset and run RT-CSP+ with same parameters
4. Compare improvements

### Exploring Edge Cases
- **High Load**: Increase arrival rate to test congestion
- **Sparse Networks**: Decrease link probability
- **Dense Networks**: Increase link probability
- **Resource Scarcity**: Use many requests with small network

## Architecture

### Components

**app.py**
- Main Dash application
- Layout definition
- Component structure

**callbacks.py**
- All interactive callbacks
- Simulation execution
- Plot updates
- Metric calculations

**__init__.py**
- Module initialization
- Exports for easy import

### Technology Stack

- **Dash**: Web framework
- **Plotly**: Interactive plotting
- **Bootstrap**: UI components
- **Font Awesome**: Icons

## Troubleshooting

### Dashboard won't start
```bash
# Check if port is already in use
lsof -i :8050

# Try a different port
python3 run_dashboard.py --port 8051
```

### Simulation fails
- Check parameter ranges
- Ensure sufficient system resources
- Review error messages in status alert

### Plots not updating
- Verify simulation completed successfully
- Check browser console for errors
- Try refreshing the page

### Slow performance
- Reduce network size
- Decrease number of requests
- Close other browser tabs
- Disable debug mode

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Advanced Usage

### Custom Host Configuration

For external access:
```bash
python3 run_dashboard.py --host 0.0.0.0 --port 8050
```

Then access from other devices at:
```
http://<your-ip-address>:8050
```

### Development Mode

Enable hot-reloading for development:
```bash
python3 run_dashboard.py --debug
```

### Integration with Other Tools

The dashboard can be embedded in Jupyter notebooks:
```python
from jupyter_dash import JupyterDash
from src.visualization.dashboard.app import create_main_layout
from src.visualization.dashboard.callbacks import register_callbacks

app = JupyterDash(__name__)
app.layout = create_main_layout()
register_callbacks(app)
app.run_server(mode='inline')
```

## Future Enhancements

Planned features:
- [ ] Real-time streaming of simulation progress
- [ ] 3D network topology visualization
- [ ] Export results to CSV/JSON
- [ ] Compare multiple algorithms side-by-side
- [ ] Save/load simulation configurations
- [ ] Historical result tracking
- [ ] Advanced filtering and search
- [ ] Custom metric definitions
- [ ] Multi-user support
- [ ] Animated network state transitions

## Support

For issues or questions:
1. Check this README
2. Review main project documentation
3. Check GitHub issues
4. Create new issue with details
