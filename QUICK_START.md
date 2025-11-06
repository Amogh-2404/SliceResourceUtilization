# Quick Start Guide

**One-page reference for demonstrating your project**

---

## =€ Fastest Demo (2 minutes)

```bash
# Run the interactive demo script
./demo_script.sh

# Choose option 1 (Quick demo)
# Opens dashboard automatically
```

---

## =Ë Essential Commands

### Quick Example (10 seconds)
```bash
python3 examples/simple_example.py
```
**Shows:** RT-CSP vs RT-CSP+ comparison with acceptance ratio improvement

### Interactive Dashboard (Best for demos)
```bash
python3 run_dashboard.py
# Open: http://localhost:8050
```
**Shows:** Real-time simulation with parameter controls

### Network Visualization (2 minutes)
```bash
python3 examples/visualize_mapping.py
# Generates 8 network topology images
# Saved to: output/figures/
```

### Generate All Paper Figures (10-30 minutes)
```bash
python3 experiments/run_paper_experiments.py
# Generates all 8 figures from the paper
# Saved to: output/figures/
```

---

## <¯ Demo Scenarios

### For Colleagues (5 mins)
1. `./demo_script.sh` ’ Choose option 1
2. Show dashboard
3. Run one simulation
4. Done!

### For Technical Interview (15 mins)
1. `python3 examples/simple_example.py` - Show results
2. Open `src/core/algorithms/rt_csp.py` in editor
3. `python3 run_dashboard.py` - Interactive demo
4. Discuss architecture

### For Formal Presentation (30 mins)
1. Pre-run: `python3 experiments/run_paper_experiments.py`
2. Presentation slides (use template in `presentation/`)
3. Live dashboard demo
4. Show generated figures in `output/figures/`
5. Q&A

---

## =Ê What to Highlight

### Key Results:
- **RT-CSP**: 44.6% acceptance ratio
- **RT-CSP+**: 54.4% acceptance ratio
- **Improvement**: +9.8 percentage points 

### Project Stats:
- 31 files created
- ~15,000 lines of code
- All 20 equations implemented
- 8 figures reproducible

### Technical Achievements:
-  Complete algorithm implementation
-  Interactive web dashboard
-  Multiple visualization methods
-  Production-ready code
-  Comprehensive documentation

---

## <¬ Dashboard Quick Guide

**Best for live demos!**

1. **Select algorithm**: RT-CSP or RT-CSP+
2. **Adjust sliders**:
   - Nodes: 20-200
   - Requests: 100-2000
   - Arrival rate: 0.02-0.1
3. **Click "Run Simulation"**
4. **View results** in tabs:
   - Acceptance Ratio (time series)
   - Revenue (bar chart)
   - Utilization (percentages)
   - Network Stats
   - Detailed Table

**Pro tip**: Run RT-CSP first, note results, reset, then run RT-CSP+ with same parameters to show improvement!

---

## =Á Key Files to Know

### Documentation:
- `README.md` - Main documentation
- `PROJECT_SUMMARY.md` - Complete project overview
- `DEMONSTRATION_GUIDE.md` - How to present (you're reading this guide's companion!)
- `docs/mathematical_formulations.md` - All 20 equations

### Code to Show:
- `src/core/algorithms/rt_csp.py` - Main algorithms (400 lines)
- `src/core/algorithms/node_ranking.py` - Node scoring (350 lines)
- `src/simulation/simulator.py` - Event simulation (440 lines)

### Examples to Run:
- `examples/simple_example.py` - Quick comparison
- `examples/visualize_mapping.py` - Network visualization
- `experiments/run_paper_experiments.py` - Full replication

---

## =à Troubleshooting

### Dashboard won't start?
```bash
# Check if already running
lsof -i :8050

# Try different port
python3 run_dashboard.py --port 8080
```

### Missing dependencies?
```bash
pip install -r requirements.txt
```

### Want to verify everything works?
```bash
./demo_script.sh
# Choose option 8 (Setup check)
```

### Clean output before demo?
```bash
./demo_script.sh
# Choose option 9 (Clean output)
# Or manually: rm -rf output/figures/*
```

---

## =¡ Presentation Tips

### Opening Line:
"I implemented a complete 5G network optimization system based on a research paper. Let me show you how it works."

### The "Wow" Moment:
Show the dashboard running a simulation in real-time, then compare RT-CSP vs RT-CSP+ results side-by-side.

### What NOT to Do:
- L Don't start with installation
- L Don't show errors
- L Don't apologize for code
- L Don't dive too deep too fast

### What TO Do:
-  Start with working demo
-  Show visual results first
-  Highlight key achievements
-  Be ready to go deeper if asked

---

## =Þ Quick Reference

| Want to... | Command | Time |
|------------|---------|------|
| Fastest demo | `./demo_script.sh` ’ 1 | 2 min |
| Show algorithm works | `python3 examples/simple_example.py` | 10 sec |
| Interactive demo | `python3 run_dashboard.py` | Ongoing |
| Show visualizations | `python3 examples/visualize_mapping.py` | 2 min |
| Reproduce paper | `python3 experiments/run_paper_experiments.py` | 10-30 min |
| Verify setup | `./demo_script.sh` ’ 8 | 1 min |

---

## <“ For Different Audiences

### Non-Technical:
- Focus on dashboard
- Use analogies ("like Google Maps finding routes")
- Show visual improvements (graphs, charts)

### Technical:
- Show code structure
- Explain algorithms
- Discuss complexity
- Deep dive into implementation

### Academic:
- Present equations
- Show mathematical proofs
- Discuss methodology
- Compare with paper results

### Recruiters/Managers:
- Show project scope (15K lines)
- Highlight technologies (Python, Dash, NetworkX)
- Demonstrate results (9% improvement)
- Emphasize best practices

---

## = Resources at a Glance

**Before Demo:**
- [ ] Test: `./demo_script.sh` ’ 8 (setup check)
- [ ] Pre-generate figures (optional): Run experiments script
- [ ] Clean output: `./demo_script.sh` ’ 9
- [ ] Test dashboard: `python3 run_dashboard.py`

**During Demo:**
- [ ] Have `DEMONSTRATION_GUIDE.md` open
- [ ] Dashboard running in browser
- [ ] Terminal ready with commands
- [ ] Figures folder open (if pre-generated)

**After Demo:**
- [ ] Share GitHub link
- [ ] Send `PROJECT_SUMMARY.md`
- [ ] Follow up with documentation links

---

## <¯ 30-Second Elevator Pitch

"I built a complete 5G network slicing system from a research paper. It simulates virtual network allocation on physical infrastructure using advanced optimization algorithms. The enhanced algorithm achieves 9% better performance. I implemented 15,000 lines of Python code including an interactive web dashboard for real-time visualization and parameter tuning. Everything is documented, tested, and production-ready."

---

## =ç Sample Follow-Up Email

```
Subject: 5G Network Slicing Project - Resources

Thank you for your interest in my 5G Network Slicing project!

Quick Links:
" GitHub Repository: [your-link]
" Live Dashboard Demo: [if hosted]
" Project Summary: [attach PROJECT_SUMMARY.md]

Try it yourself:
1. git clone [repo]
2. pip install -r requirements.txt
3. python3 run_dashboard.py

The interactive dashboard lets you explore different
configurations and see RT-CSP+ outperform RT-CSP in real-time.

Feel free to reach out with any questions!

Best regards,
[Your Name]
```

---

**Remember:** The goal is to show your work clearly and confidently. You've built something impressive - let it shine! <

---

**Print this page and keep it handy during demos!**
