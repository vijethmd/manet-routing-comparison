#!/usr/bin/env python3
"""
Plot the AODV / OLSR / DSDV MANET experiment results (used ONLY for analysis/plotting).

Reads the CSV files written by run_experiments.sh:
    results/csv/exp_A_nodes.csv   (varying number of nodes)
    results/csv/exp_B_speed.csv   (varying node speed)
    results/csv/exp_C_load.csv    (varying packet rate / traffic load)

Each parameter value is simulated several times (different random runs) for
every protocol. The graphs show one line per protocol: the MEAN over the runs,
with error bars = standard deviation for the delivery ratio.

Outputs PNG graphs to results/graphs/ and an averaged table per experiment
(mean, standard deviation and 95% confidence half-width per protocol and
parameter value) to results/csv/*_mean.csv.

Usage:  python3 scripts/plot_results.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no GUI window needed, just save files
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT / "results" / "csv"
GRAPH_DIR = PROJECT / "results" / "graphs"

METRICS = {
    "pdr_pct": "Packet Delivery Ratio (%)",
    "throughput_kbps": "Throughput (kbps)",
    "avg_delay_ms": "Average End-to-End Delay (ms)",
    "avg_jitter_ms": "Average Jitter (ms)",
    "lost_packets": "Packet Loss (packets)",
    "loss_ratio_pct": "Packet Loss Ratio (%)",
    "ctrl_packets": "Routing Control Packets",
    "nrl": "Normalised Routing Load",
}
SHORT = {"pdr_pct": "pdr", "throughput_kbps": "throughput", "avg_delay_ms": "delay",
         "avg_jitter_ms": "jitter", "lost_packets": "packet_loss", "loss_ratio_pct": "loss_ratio",
         "ctrl_packets": "overhead", "nrl": "nrl"}
COLORS = {"AODV": "#1f5fa8", "OLSR": "#c8611b", "DSDV": "#2e8b57"}
MARKERS = {"AODV": "o", "OLSR": "s", "DSDV": "^"}

# (csv file, x column, x label, file prefix, metrics to plot)
EXPERIMENTS = [
    ("exp_A_nodes.csv", "nodes", "Number of Nodes", "nodes",
     ["pdr_pct", "throughput_kbps", "avg_delay_ms", "avg_jitter_ms", "ctrl_packets", "nrl"]),
    ("exp_B_speed.csv", "speed_mps", "Node Speed (m/s)", "speed",
     ["pdr_pct", "avg_delay_ms", "avg_jitter_ms", "throughput_kbps", "ctrl_packets", "nrl"]),
    ("exp_C_load.csv", "packet_rate_pps", "Packet Rate (packets/s)", "load",
     ["pdr_pct", "throughput_kbps", "avg_delay_ms", "avg_jitter_ms", "loss_ratio_pct", "nrl"]),
]


def ci95(series):
    """Half-width of the 95% confidence interval of the mean (Student t)."""
    n = series.count()
    if n < 2:
        return 0.0
    return stats.t.ppf(0.975, n - 1) * series.std() / n ** 0.5


def plot_one(mean, std, x, xlabel, metric, out_file, logx=False):
    fig, ax = plt.subplots(figsize=(6, 4))
    span = mean[x].max() - mean[x].min()
    for i, (proto, m) in enumerate(mean.groupby("protocol")):
        s = std[std["protocol"] == proto]
        yerr = s[metric].fillna(0) if metric == "pdr_pct" else None
        shift = i - 1  # nudge the protocols apart so their error bars do not overlap
        xs = m[x] * 1.06 ** shift if logx else m[x] + 0.012 * span * shift
        ax.errorbar(xs, m[metric], yerr=yerr, marker=MARKERS.get(proto, "o"), capsize=4,
                    linewidth=2, color=COLORS.get(proto), label=proto, elinewidth=1, alpha=0.9)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(METRICS[metric])
    ax.set_title(f"{xlabel} vs {METRICS[metric].split(' (')[0]}")
    if logx:  # packet rates span 10..800, so use a log scale
        ax.set_xscale("log")
    ticks = sorted(mean[x].unique())
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{v:g}" for v in ticks])
    ax.minorticks_off()
    ax.grid(True, alpha=0.3)
    if metric in ("pdr_pct", "loss_ratio_pct"):
        ax.set_ylim(0, 105)
    else:
        ax.set_ylim(bottom=0)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_file, dpi=150)
    plt.close(fig)


def main():
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    made = 0
    for csv_name, x, xlabel, prefix, metrics in EXPERIMENTS:
        path = CSV_DIR / csv_name
        if not path.exists():
            print(f"[skip] {path} not found (run that experiment first)")
            continue
        df = pd.read_csv(path)
        if df.empty:
            print(f"[skip] {path} is empty")
            continue

        cols = list(METRICS)
        groups = df.groupby(["protocol", x])[cols]
        mean = groups.mean().reset_index()
        std = groups.std().reset_index()
        ci = groups.agg(ci95).reset_index()

        table = mean.copy()
        for c in cols:
            table[f"{c}_sd"] = std[c]
            table[f"{c}_ci95"] = ci[c]
        mean_file = CSV_DIR / csv_name.replace(".csv", "_mean.csv")
        table.round(3).to_csv(mean_file, index=False)
        runs = df.groupby(["protocol", x]).size().iloc[0]
        print(f"\n{csv_name}  (mean of {runs} runs per point)")
        print(mean.round(2).to_string(index=False))

        for metric in metrics:
            out = GRAPH_DIR / f"{prefix}_vs_{SHORT[metric]}.png"
            plot_one(mean, std, x, xlabel, metric, out, logx=(prefix == "load"))
            made += 1

    print(f"\nSaved {made} graphs to {GRAPH_DIR}")


if __name__ == "__main__":
    main()
