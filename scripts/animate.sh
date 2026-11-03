#!/usr/bin/env bash
#
# Make a NetAnim animation of ONE simulation and open NetAnim.
#
# Examples:
#   ./scripts/animate.sh                      # AODV, run 2
#   ./scripts/animate.sh OLSR 2               # OLSR on the same topology
#   ./scripts/animate.sh AODV 3 --nodes=20    # extra options go to the simulation
#
# In NetAnim: click the folder icon ("Open XML trace file"), choose the file
# printed below, then press Play. Green = source, red = destination, blue = relays.
#
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NETANIM="${NETANIM:-$HOME/ns3-project/netanim/build/bin/netanim}"
PROTO="${1:-AODV}"
RUN="${2:-2}"
shift $(($# > 2 ? 2 : $#))
FILE="results/netanim/$(echo "$PROTO" | tr '[:upper:]' '[:lower:]')-run$RUN.xml"

"$PROJECT_DIR/scripts/run_single.sh" --protocol="$PROTO" --run="$RUN" --animate --animFile="$FILE" "$@"

echo
echo "Animation file: $PROJECT_DIR/$FILE"
if [ -x "$NETANIM" ]; then
    echo "Opening NetAnim: click the folder icon, open the file above, then press Play."
    "$NETANIM" >/dev/null 2>&1 &
else
    echo "NetAnim not found at $NETANIM (set NETANIM=/path/to/netanim)"
fi
