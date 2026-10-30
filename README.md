# Performance Analysis of AODV in a MANET Using NS-3: Comparison with OLSR and DSDV

This project extends the Team 11 Network Programming AAT project
[tanmayagr2021/manet-aodv-project](https://github.com/tanmayagr2021/manet-aodv-project).
The original project measured how the **AODV** routing protocol performs in a mobile ad hoc network
(MANET) when the number of nodes, the node speed and the traffic load change. This version keeps that
study exactly (AODV results are identical, run for run) and adds:

| Addition | Why |
|---|---|
| **OLSR and DSDV** as baselines (`--protocol=AODV\|OLSR\|DSDV`) | Compare the reactive AODV with two proactive protocols under the same scenarios |
| **Routing overhead**: control packets sent and Normalised Routing Load (NRL) | The cost of finding routes, which the original study did not measure |
| **Jitter** (mean delay variation) | Listed in the AAT guidelines as an observation metric |
| **Packets dropped at the source** | OLSR and DSDV drop packets when they have no route; these must count as lost |
| **95% confidence intervals and paired significance tests** (`scripts/analyse.py`) | Show which differences are reliable with 10 runs |

## 1. Simulation scenario (defaults)

| Setting | Value |
|---|---|
| Simulator | ns-3.48 (C++) |
| Nodes | 10 mobile nodes in 700 m × 700 m |
| Wi-Fi | IEEE 802.11b, ad-hoc mode, 11 Mbps |
| Radio range | 250 m (Friis propagation + range cutoff) |
| Mobility | Random Waypoint, 5 m/s, 0 s pause |
| Network layer / routing | IPv4 with AODV (UDP port 654), OLSR (698) or DSDV (269), ns-3 default settings |
| Traffic | One UDP CBR flow, node 0 → node N−1, 512-byte packets, 4 packets/s |
| Simulation time | 60 s (traffic from 2 s to 59 s) |
| Repetitions | 10 runs per setting and protocol; run *k* uses the same positions and movement for every protocol |

| Experiment | Parameter changed | Values |
|---|---|---|
| A | Number of nodes | 5, 10, 15, 20 |
| B | Node speed | 1, 5, 10, 15 m/s |
| C | Traffic load (CBR rate) | 10, 50, 100, 200, 400, 800 packets/s |

14 settings × 3 protocols × 10 runs = **420 simulations**.

## 2. Requirements

| Software | Version used |
|---|---|
| macOS on Apple Silicon (any Linux also works) | macOS 15.6.1 |
| Apple clang / Xcode Command Line Tools | clang 16.0.0 |
| CMake (ns-3.48 needs ≥ 3.25) | 4.4.3 |
| Python 3 with pandas, matplotlib and scipy | 3.13.7 |
| ns-3 | **3.48** |

## 3. Setup

```bash
# 1. ns-3 (official release), built only with the modules this project needs
mkdir -p ~/ns3-project && cd ~/ns3-project
git clone --depth 1 --branch ns-3.48 https://gitlab.com/nsnam/ns-3-dev.git ns-3
cd ns-3
./ns3 configure -d optimized --disable-examples --disable-tests --disable-python-bindings \
    --enable-modules="aodv;olsr;dsdv;flow-monitor;wifi;mobility;internet;applications"

# 2. Link this project's src/ folder into ns-3's scratch/ folder
ln -s /path/to/manet-routing-comparison/src scratch/manet-routing

# 3. Build (a few minutes)
./ns3 build
```

ns-3 builds every program in `scratch/`, so it compiles `src/manet-routing.cc` as the program
**`manet-routing`** while the code stays in this project. If ns-3 is not in `~/ns3-project/ns-3`,
set `NS3_DIR=/path/to/ns-3` when running the scripts.

## 4. Project structure

```
manet-routing-comparison/
├── src/manet-routing.cc        the simulation (C++)
├── scripts/
│   ├── run_single.sh           build + run one simulation
│   ├── plot_results.py         graphs + mean/SD/95% CI tables
│   └── analyse.py              paired significance tests between protocols
├── run_experiments.sh          runs experiments A, B, C for every protocol, then plots
├── results/
│   ├── csv/                    one row per run, averages, test results
│   ├── graphs/                 PNG graphs (one line per protocol)
│   └── summaries/              text summary of every run
└── report/                     AAT report (PDF and Word)
```

## 5. Running

```bash
./scripts/run_single.sh                                    # AODV, defaults
./scripts/run_single.sh --protocol=OLSR --nodes=20 --run=3  # any option
./scripts/run_single.sh --PrintHelp                        # list all options

./run_experiments.sh                    # all 420 runs, then graphs (about 10 minutes)
./run_experiments.sh A                  # only experiment A (also B or C)
PROTOCOLS="AODV OLSR" RUNS=20 ./run_experiments.sh
python3 scripts/plot_results.py         # redraw graphs from the CSV files
python3 scripts/analyse.py              # significance tests
```

| Option | Meaning | Default |
|---|---|---|
| `--protocol` | routing protocol: AODV, OLSR or DSDV | AODV |
| `--nodes` | number of mobile nodes | 10 |
| `--simTime` | simulation time (s) | 60 |
| `--packetSize` / `--packetRate` | CBR payload (bytes) / packets per second | 512 / 4 |
| `--speed` / `--pause` | node speed (m/s) / pause at each waypoint (s) | 5 / 0 |
| `--area` / `--range` | side of the square area / radio range (m) | 700 / 250 |
| `--seed` / `--run` | random seed / run number (same values = same result) | 1 / 1 |
| `--experiment`, `--csv`, `--summary` | CSV label, CSV file, summary file | single, results/csv/single_results.csv, results/summaries/single_summary.txt |

## 6. Metrics

All data metrics are for the CBR flow only; routing control packets are excluded.

| Metric | Definition |
|---|---|
| Tx packets | Packets generated by the source application (client "Tx" trace) |
| Rx packets | Packets received at the destination (FlowMonitor) |
| PDR (%) | Rx / Tx × 100 |
| Loss | Tx − Rx; loss ratio = 100 − PDR |
| Throughput (kbps) | Received bytes (IP layer, 540 bytes per packet) × 8 / 57 s / 1000 |
| Average delay (ms) | Mean (receive time − send time) of received packets |
| Average jitter (ms) | FlowMonitor jitterSum / (Rx − 1): mean change in delay between consecutive packets |
| Control packets | Routing packets transmitted by all nodes at the IP layer (originated and forwarded, broadcast and unicast), counted on the protocol's UDP port with the `Ipv4L3Protocol/Tx` trace |
| NRL | Control packets / Rx packets |
| Source drops | Packets dropped at the source because the protocol had no route |

CSV columns: `experiment, protocol, nodes, sim_time_s, packet_size_B, packet_rate_pps, speed_mps,
pause_s, area_m, seed, run, tx_packets, rx_packets, lost_packets, loss_ratio_pct, pdr_pct,
throughput_kbps, avg_delay_ms, avg_jitter_ms, ctrl_packets, ctrl_bytes, nrl, source_drops`

## 7. Results (mean of 10 runs)

**Experiment A: number of nodes** (5 m/s, 4 packets/s)

| Nodes | Protocol | PDR (%) | Throughput (kbps) | Delay (ms) | Jitter (ms) | Control pkts | NRL | Source drops |
|---|---|---|---|---|---|---|---|---|
| 5 | AODV | 74.4 | 12.9 | 44.2 | 15.5 | 313 | 3.79 | 0.0 |
|  | OLSR | 69.6 | 12.0 | 1.0 | 0.2 | 160 | 1.91 | 59.4 |
|  | DSDV | 59.3 | 10.2 | 0.6 | 0.0 | 68 | 0.36 | 0.0 |
| 10 | AODV | 79.5 | 13.7 | 40.5 | 13.8 | 630 | 5.53 | 0.0 |
|  | OLSR | 68.2 | 11.8 | 1.7 | 0.5 | 353 | 3.14 | 58.0 |
|  | DSDV | 65.5 | 11.3 | 20.8 | 4.5 | 325 | 4.19 | 0.0 |
| 15 | AODV | 95.7 | 16.5 | 12.3 | 10.2 | 960 | 4.42 | 0.0 |
|  | OLSR | 85.0 | 14.7 | 1.5 | 0.5 | 562 | 2.94 | 18.3 |
|  | DSDV | 84.1 | 14.5 | 14.8 | 5.4 | 843 | 4.62 | 0.0 |
| 20 | AODV | 96.7 | 16.7 | 20.2 | 11.1 | 1248 | 5.68 | 0.0 |
|  | OLSR | 87.9 | 15.2 | 1.4 | 0.4 | 753 | 3.89 | 16.8 |
|  | DSDV | 85.4 | 14.8 | 2.3 | 1.2 | 1542 | 8.31 | 0.0 |

**Experiment B: node speed** (10 nodes, 4 packets/s)

| Speed (m/s) | Protocol | PDR (%) | Throughput (kbps) | Delay (ms) | Jitter (ms) | Control pkts | NRL | Source drops |
|---|---|---|---|---|---|---|---|---|
| 1 | AODV | 75.9 | 13.1 | 22.3 | 8.3 | 631 | 3.28 | 0.0 |
|  | OLSR | 67.1 | 11.6 | 1.6 | 0.1 | 343 | 2.19 | 72.6 |
|  | DSDV | 70.4 | 12.2 | 17.7 | 10.6 | 261 | 1.51 | 0.0 |
| 5 | AODV | 79.5 | 13.7 | 40.5 | 13.8 | 630 | 5.53 | 0.0 |
|  | OLSR | 68.2 | 11.8 | 1.7 | 0.5 | 353 | 3.14 | 58.0 |
|  | DSDV | 65.5 | 11.3 | 20.8 | 4.5 | 325 | 4.19 | 0.0 |
| 10 | AODV | 72.9 | 12.6 | 75.0 | 27.3 | 648 | 10.18 | 0.0 |
|  | OLSR | 50.5 | 8.7 | 3.9 | 3.0 | 353 | 6.78 | 68.1 |
|  | DSDV | 51.0 | 8.8 | 35.1 | 8.0 | 332 | 6.26 | 0.0 |
| 15 | AODV | 75.2 | 13.0 | 90.9 | 21.2 | 664 | 4.59 | 0.0 |
|  | OLSR | 50.0 | 8.6 | 4.3 | 2.9 | 356 | 3.75 | 69.9 |
|  | DSDV | 47.3 | 8.2 | 79.7 | 17.5 | 339 | 3.64 | 0.0 |

**Experiment C: traffic load** (10 nodes, 5 m/s)

| Rate (pkt/s) | Protocol | PDR (%) | Throughput (kbps) | Delay (ms) | Jitter (ms) | Control pkts | NRL | Source drops |
|---|---|---|---|---|---|---|---|---|
| 10 | AODV | 79.1 | 34.2 | 28.6 | 6.8 | 633 | 2.26 | 0.0 |
|  | OLSR | 68.3 | 29.5 | 1.6 | 0.2 | 353 | 1.25 | 144.6 |
|  | DSDV | 69.5 | 30.0 | 10.4 | 2.0 | 327 | 1.04 | 0.0 |
| 50 | AODV | 78.8 | 170.2 | 5.4 | 0.6 | 637 | 0.45 | 0.0 |
|  | OLSR | 67.7 | 146.3 | 2.5 | 0.7 | 353 | 0.27 | 722.1 |
|  | DSDV | 66.0 | 142.5 | 2.9 | 1.1 | 322 | 0.33 | 0.0 |
| 100 | AODV | 78.4 | 338.5 | 3.5 | 0.2 | 645 | 0.23 | 0.0 |
|  | OLSR | 67.5 | 291.8 | 2.1 | 0.2 | 352 | 0.13 | 1495.4 |
|  | DSDV | 65.0 | 281.0 | 2.8 | 0.9 | 321 | 0.15 | 0.0 |
| 200 | AODV | 77.1 | 666.0 | 2.1 | 0.1 | 1081 | 0.22 | 0.0 |
|  | OLSR | 67.2 | 580.2 | 2.0 | 0.1 | 353 | 0.07 | 3046.9 |
|  | DSDV | 65.3 | 564.4 | 6.9 | 0.4 | 314 | 0.07 | 0.0 |
| 400 | AODV | 71.2 | 1230.8 | 108.9 | 1.0 | 1054 | 0.09 | 0.0 |
|  | OLSR | 62.0 | 1071.3 | 109.6 | 1.6 | 352 | 0.04 | 6639.5 |
|  | DSDV | 62.3 | 1077.1 | 125.0 | 0.5 | 311 | 0.03 | 0.0 |
| 800 | AODV | 57.2 | 1978.3 | 173.5 | 2.6 | 1634 | 0.12 | 0.0 |
|  | OLSR | 49.7 | 1718.8 | 208.0 | 1.9 | 348 | 0.04 | 16817.6 |
|  | DSDV | 53.9 | 1863.3 | 239.4 | 1.6 | 304 | 0.03 | 0.0 |

### Main findings

- **AODV delivers the most packets**: 77.9% on average over the 13 distinct settings, against 66.2% for
  OLSR and 65.0% for DSDV. Paired t-tests (runs share topologies) show AODV significantly higher in
  12 of 13 settings than OLSR and 9 of 13 than DSDV, and never significantly lower.
- **Mobility separates the protocols most**: from 1 to 15 m/s AODV stays near 75%, while OLSR falls
  from 67.1% to 50.0% and DSDV from 70.4% to 47.3%. Proactive tables (OLSR every 2–5 s, DSDV every
  15 s) go stale between updates; AODV repairs routes on demand.
- **The price is overhead and delay**: AODV sends about twice as many control packets (630 vs 353 and
  325 per run in the default scenario), and it buffers packets during route discovery, so its mean
  delay and jitter are higher. OLSR's delay is lowest because it drops packets that have no route;
  72–75% of all OLSR losses are such source drops.
- **Heavy load congests every protocol**: at 800 packets/s PDR falls to 57.2% (AODV), 53.9% (DSDV)
  and 49.7% (OLSR).
- **Validation**: the 140 AODV runs are identical to the original project; Tx = 57 s × rate and
  loss = 100 − PDR in all 420 runs; throughput equals offered load × PDR; OLSR's overhead matches
  N × 30 HELLOs plus TC messages.

Graphs are in `results/graphs/`, per-point mean/SD/95% CI in `results/csv/*_mean.csv`, and all
pairwise tests in `results/csv/protocol_tests.csv`.

## 8. Report and presentation

| File | Contents |
|---|---|
| `report/NP_AAT_Report_Team11_AODV_OLSR_DSDV.pdf` | AAT report (26 pages) following the AAT Report Guidelines 2026-27 |
| `report/NP_AAT_Report_Team11_AODV_OLSR_DSDV.docx` | Editable Word version of the report |
| `presentation/AODV_OLSR_DSDV_MANET_Team11.pptx` | 17-slide presentation with speaker notes |


## Limitations

- The 250 m range cutoff is an idealised radio model; real radios fade gradually.
- One CBR flow only; Random Waypoint is a synthetic mobility model.
- All protocols use the ns-3 default settings and the same 2 s start of traffic, so the proactive
  protocols have little time to build their tables before the first packets.
- 10 runs per point leave wide confidence intervals; use `RUNS=20` or more for tighter results.
