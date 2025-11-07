#!/bin/bash

# =============================================================================
# Project Demonstration Helper Script
# =============================================================================
# This script provides interactive menus for different demonstration scenarios
# Usage: ./demo_script.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN} $1${NC}"
}

print_info() {
    echo -e "${YELLOW}� $1${NC}"
}

print_error() {
    echo -e "${RED} $1${NC}"
}

press_enter() {
    echo ""
    read -p "Press Enter to continue..."
}

# Check if in project root
if [ ! -f "run_dashboard.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Main menu
show_main_menu() {
    clear
    print_header "5G Network Slice Provisioning - Demo Helper"
    echo ""
    echo "Choose a demonstration scenario:"
    echo ""
    echo "  1) Quick 5-minute demo \(Dashboard only\)"
    echo "  2) 15-minute technical demo \(Examples + Dashboard\)"
    echo "  3) Full demo \(Generate figures + Dashboard\)"
    echo "  4) Network visualization demo"
    echo "  5) Generate all paper figures \(takes 10-30 mins\)"
    echo "  6) Launch dashboard only"
    echo "  7) Run simple example"
    echo "  8) Setup check \(verify installation\)"
    echo "  9) Clean output directory"
    echo "  0) Exit"
    echo ""
    read -p "Enter choice [0-9]: " choice
    echo ""

    case $choice in
        1) quick_demo ;;
        2) technical_demo ;;
        3) full_demo ;;
        4) network_viz_demo ;;
        5) generate_figures ;;
        6) launch_dashboard ;;
        7) run_simple_example ;;
        8) setup_check ;;
        9) clean_output ;;
        0) exit 0 ;;
        *) print_error "Invalid choice"; sleep 2; show_main_menu ;;
    esac
}

# Demo scenarios
quick_demo() {
    print_header "Quick 5-Minute Demo"
    echo ""
    print_info "This demo will:"
    echo "  1. Show project structure"
    echo "  2. Launch interactive dashboard"
    echo "  3. Guide you through a quick simulation"
    echo ""
    press_enter

    print_info "Step 1: Project Structure"
    tree -L 2 -I '__pycache__|*.pyc|output' || ls -R | grep ":$" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/'
    press_enter

    print_info "Step 2: Launching Dashboard"
    print_info "The dashboard will open at http://localhost:8050"
    print_info "Try these steps in the browser:"
    echo "  • Select RT-CSP algorithm"
    echo "  • Set 50 nodes, 200 requests"
    echo "  • Click 'Run Simulation'"
    echo "  • Note the acceptance ratio"
    echo "  • Click 'Reset'"
    echo "  • Switch to RT-CSP+"
    echo "  • Run again and compare results!"
    echo ""
    print_info "Press Ctrl+C in this terminal to stop the dashboard when done"
    echo ""
    press_enter

    python3 run_dashboard.py

    show_main_menu
}

technical_demo() {
    print_header "15-Minute Technical Demo"
    echo ""

    print_info "Step 1: Quick Example \(2 mins\)"
    print_info "Running comparison between RT-CSP and RT-CSP+..."
    echo ""
    python3 examples/simple_example.py
    press_enter

    print_info "Step 2: Code Overview \(Opening key files\)"
    echo ""
    echo "Opening main algorithm file..."
    echo "File: src/core/algorithms/rt_csp.py"
    echo ""
    print_info "Review the code structure and documentation"
    press_enter

    print_info "Step 3: Dashboard Demo"
    print_info "Launching interactive dashboard..."
    echo ""
    echo "Try comparing different configurations:"
    echo "  • Different network sizes \(20, 50, 100 nodes\)"
    echo "  • Different arrival rates \(0.02, 0.04, 0.08\)"
    echo "  • RT-CSP vs RT-CSP+"
    echo ""
    print_info "Press Ctrl+C to stop when done"
    press_enter

    python3 run_dashboard.py

    show_main_menu
}

full_demo() {
    print_header "Full Demonstration"
    echo ""
    print_error "WARNING: This will take 10-30 minutes to generate all figures!"
    read -p "Continue? \(y/n\): " confirm

    if [ "$confirm" != "y" ]; then
        show_main_menu
        return
    fi

    print_info "Step 1: Running paper experiments..."
    python3 experiments/run_paper_experiments.py
    print_success "Figures generated in output/figures/"
    press_enter

    print_info "Step 2: Opening figure directory..."
    if command -v open &> /dev/null; then
        open output/figures/
    elif command -v xdg-open &> /dev/null; then
        xdg-open output/figures/
    else
        print_info "Please open output/figures/ manually"
    fi
    press_enter

    print_info "Step 3: Launching dashboard..."
    python3 run_dashboard.py

    show_main_menu
}

network_viz_demo() {
    print_header "Network Visualization Demo"
    echo ""
    print_info "Generating network visualizations..."
    print_info "This will create:"
    echo "  • Physical network topology"
    echo "  • Slice request topology"
    echo "  • Slice-to-physical mapping"
    echo "  • Resource utilization heatmaps"
    echo ""
    press_enter

    python3 examples/visualize_mapping.py

    print_success "Visualizations saved to output/figures/"
    print_info "Opening figure directory..."

    if command -v open &> /dev/null; then
        open output/figures/
    elif command -v xdg-open &> /dev/null; then
        xdg-open output/figures/
    else
        print_info "Please open output/figures/ manually"
    fi

    press_enter
    show_main_menu
}

generate_figures() {
    print_header "Generate All Paper Figures"
    echo ""
    print_error "WARNING: This takes 10-30 minutes!"
    print_info "This will:"
    echo "  • Run 4 different experiment configurations"
    echo "  • Compare RT-CSP vs RT-CSP+"
    echo "  • Generate all 8 figures from the paper"
    echo ""
    read -p "Continue? \(y/n\): " confirm

    if [ "$confirm" != "y" ]; then
        show_main_menu
        return
    fi

    python3 experiments/run_paper_experiments.py

    print_success "All figures generated!"
    print_info "Location: output/figures/"

    if command -v open &> /dev/null; then
        open output/figures/
    elif command -v xdg-open &> /dev/null; then
        xdg-open output/figures/
    fi

    press_enter
    show_main_menu
}

launch_dashboard() {
    print_header "Launch Interactive Dashboard"
    echo ""
    print_info "Starting dashboard at http://localhost:8050"
    print_info "Press Ctrl+C to stop"
    echo ""
    press_enter

    python3 run_dashboard.py

    show_main_menu
}

run_simple_example() {
    print_header "Run Simple Example"
    echo ""
    print_info "Running RT-CSP vs RT-CSP+ comparison..."
    echo ""

    python3 examples/simple_example.py

    print_success "Example completed!"
    press_enter
    show_main_menu
}

setup_check() {
    print_header "Setup Verification"
    echo ""

    print_info "Checking Python version..."
    python3 --version
    if [ $? -eq 0 ]; then
        print_success "Python 3 installed"
    else
        print_error "Python 3 not found"
    fi
    echo ""

    print_info "Checking dependencies..."
    python3 -c "import networkx, numpy, matplotlib, dash, plotly" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "All required packages installed"
    else
        print_error "Some packages missing. Run: pip install -r requirements.txt"
    fi
    echo ""

    print_info "Checking project structure..."
    if [ -d "src" ] && [ -d "examples" ] && [ -d "experiments" ]; then
        print_success "Project structure intact"
    else
        print_error "Project structure incomplete"
    fi
    echo ""

    print_info "Testing quick import..."
    python3 -c "from src.simulation import generate_physical_network; print\('Import test passed'\)" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Imports working correctly"
    else
        print_error "Import error detected"
    fi
    echo ""

    print_info "Creating output directory if needed..."
    mkdir -p output/figures
    print_success "Output directory ready"
    echo ""

    print_success "Setup check complete!"
    press_enter
    show_main_menu
}

clean_output() {
    print_header "Clean Output Directory"
    echo ""
    print_error "This will delete all generated figures!"
    read -p "Are you sure? \(y/n\): " confirm

    if [ "$confirm" != "y" ]; then
        show_main_menu
        return
    fi

    rm -rf output/figures/*
    print_success "Output directory cleaned"

    print_info "Also clean Python cache files?"
    read -p "\(y/n\): " confirm

    if [ "$confirm" == "y" ]; then
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        find . -type f -name "*.pyc" -delete 2>/dev/null
        print_success "Cache files cleaned"
    fi

    press_enter
    show_main_menu
}

# Start the script
show_main_menu
