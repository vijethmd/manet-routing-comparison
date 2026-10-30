#!/usr/bin/env bash
#
# Run all MANET experiments for AODV, OLSR and DSDV and draw the graphs.
#
#   Experiment A: number of nodes   (5, 10, 15, 20)       speed 5 m/s, 4 pkt/s
#   Experiment B: node speed        (1, 5, 10, 15 m/s)    10 nodes,   4 pkt/s
#   Experiment C: traffic load      (10, 50, 100, 200, 400, 800 pkt/s) 10 nodes, 5 m/s
#
# Every parameter value is simulated RUNS times (different random run numbers)
# for every protocol in PROTOCOLS, and the graphs show the average, so one
# lucky/unlucky topology does not dominate the result. Runs with the same run
# number use the same node positions and movement for every protocol.
#
# Usage:
#   ./run_experiments.sh            # run A, B and C, then plot
#   ./run_experiments.sh A          # run only experiment A (also B / C)
#   RUNS=5 SIM_TIME=100 ./run_experiments.sh
#   PROTOCOLS="AODV OLSR" ./run_experiments.sh
#
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
NS3_DIR="${NS3_DIR:-$HOME/ns3-project/ns-3}"
RUNS="${RUNS:-10}"           # repetitions per parameter value
PROTOCOLS="${PROTOCOLS:-AODV OLSR DSDV}"
SIM_TIME="${SIM_TIME:-60}"   # seconds
PACKET_SIZE="${PACKET_SIZE:-512}"
WHICH="${1:-all}"

CSV_DIR="$PROJECT_DIR/results/csv"
SUM_DIR="$PROJECT_DIR/results/summaries"
mkdir -p "$CSV_DIR" "$SUM_DIR" "$PROJECT_DIR/results/graphs"

if [ ! -x "$NS3_DIR/ns3" ]; then
    echo "ERROR: ns-3 not found at $NS3_DIR (set NS3_DIR=/path/to/ns-3)" >&2
    exit 1
fi

echo ">>> Building manet-routing ..."
(cd "$NS3_DIR" && ./ns3 build manet-routing)

# run_sim <experiment-label> <csv-file> <summary-file> [extra --options...]
run_sim() {
    local label="$1" csv="$2" summary="$3"
    shift 3
    (cd "$NS3_DIR" && ./ns3 run --no-build --cwd="$PROJECT_DIR" \
        "manet-routing --experiment=$label --csv=$csv --summary=$summary \
         --simTime=$SIM_TIME --packetSize=$PACKET_SIZE $*") > /dev/null
}

# run_experiment <label> <csv name> <option name> <values...> -- <fixed options...>
run_experiment() {
    local label="$1" csvname="$2" option="$3"
    shift 3
    local values=()
    while [ "$1" != "--" ]; do values+=("$1"); shift; done
    shift
    local fixed="$*"
    local csv="results/csv/$csvname"
    rm -f "$PROJECT_DIR/$csv" "$SUM_DIR"/exp_"$label"_*.txt
    echo ">>> Experiment $label: varying --$option over (${values[*]}), $RUNS runs each, protocols: $PROTOCOLS"
    for proto in $PROTOCOLS; do
        for v in "${values[@]}"; do
            for run in $(seq 1 "$RUNS"); do
                printf "    %s %s=%-4s run=%s\n" "$proto" "$option" "$v" "$run"
                run_sim "$label" "$csv" \
                    "results/summaries/exp_${label}_${proto}_${option}${v}_run${run}.txt" \
                    "--protocol=$proto --$option=$v --run=$run $fixed"
            done
        done
    done
    echo "    -> $csv ($(($(wc -l < "$PROJECT_DIR/$csv") - 1)) rows)"
}

case "$WHICH" in all|A)
    run_experiment A exp_A_nodes.csv nodes 5 10 15 20 -- --speed=5 --packetRate=4 ;;
esac
case "$WHICH" in all|B)
    run_experiment B exp_B_speed.csv speed 1 5 10 15 -- --nodes=10 --packetRate=4 ;;
esac
case "$WHICH" in all|C)
    run_experiment C exp_C_load.csv packetRate 10 50 100 200 400 800 -- --nodes=10 --speed=5 ;;
esac

echo ">>> Plotting ..."
python3 "$PROJECT_DIR/scripts/plot_results.py"
echo ">>> Done. CSV: $CSV_DIR   Graphs: $PROJECT_DIR/results/graphs"
