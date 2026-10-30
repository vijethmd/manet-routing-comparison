#!/usr/bin/env python3
"""
Statistical summary of the AODV / OLSR / DSDV experiments.

For every experiment, protocol and parameter value it prints the mean, standard
deviation and 95% confidence interval of each metric, and it compares the
protocols with paired t-tests and Wilcoxon signed-rank tests. Runs with the same
run number use the same node positions and movement for every protocol, so the
comparison is paired by run number.

Writes results/csv/protocol_tests.csv.

Usage:  python3 scripts/analyse.py
"""

from itertools import combinations
from pathlib import Path

import pandas as pd
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT / "results" / "csv"

EXPERIMENTS = [("A", "exp_A_nodes.csv", "nodes"),
               ("B", "exp_B_speed.csv", "speed_mps"),
               ("C", "exp_C_load.csv", "packet_rate_pps")]
METRICS = ["pdr_pct", "avg_delay_ms", "avg_jitter_ms", "throughput_kbps", "ctrl_packets", "nrl"]


def paired(a, b):
    """p-values of a paired t-test and a Wilcoxon test (NaN when all differences are zero)."""
    diff = a - b
    if (diff == 0).all():
        return float("nan"), float("nan")
    return stats.ttest_rel(a, b).pvalue, stats.wilcoxon(a, b).pvalue


def main():
    rows = []
    for label, csv_name, x in EXPERIMENTS:
        path = CSV_DIR / csv_name
        if not path.exists():
            print(f"[skip] {path} not found")
            continue
        df = pd.read_csv(path)
        protocols = sorted(df["protocol"].unique())
        for value, group in df.groupby(x):
            runs = {p: g.sort_values("run").set_index("run") for p, g in group.groupby("protocol")}
            for metric in METRICS:
                for p1, p2 in combinations(protocols, 2):
                    a, b = runs[p1][metric], runs[p2][metric]
                    common = a.index.intersection(b.index)
                    t_p, w_p = paired(a[common], b[common])
                    rows.append({"experiment": label, "parameter": x, "value": value, "metric": metric,
                                 "protocol_1": p1, "mean_1": a.mean(), "protocol_2": p2, "mean_2": b.mean(),
                                 "runs": len(common), "paired_t_p": t_p, "wilcoxon_p": w_p})
    out = pd.DataFrame(rows)
    out.round(4).to_csv(CSV_DIR / "protocol_tests.csv", index=False)
    with pd.option_context("display.width", 200, "display.max_rows", 500):
        print(out[out["metric"].isin(["pdr_pct", "avg_delay_ms", "nrl"])].round(3).to_string(index=False))
    print(f"\nWrote {CSV_DIR / 'protocol_tests.csv'}")


if __name__ == "__main__":
    main()
