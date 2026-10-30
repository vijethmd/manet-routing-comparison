#!/usr/bin/env bash
#
# Build and run ONE simulation. Any options are passed to the simulation.
#
# Examples:
#   ./scripts/run_single.sh
#   ./scripts/run_single.sh --nodes=20 --speed=10 --simTime=100
#   ./scripts/run_single.sh --protocol=OLSR
#   ./scripts/run_single.sh --PrintHelp
#
# Results are appended to results/csv/single_results.csv and the summary is
# written to results/summaries/single_summary.txt
#
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NS3_DIR="${NS3_DIR:-$HOME/ns3-project/ns-3}"
mkdir -p "$PROJECT_DIR/results/csv" "$PROJECT_DIR/results/summaries"
cd "$NS3_DIR"
./ns3 run --cwd="$PROJECT_DIR" "manet-routing $*"
