#!/usr/bin/env python3
# Reproduces the ablation and cross-sector tables of the CIPO-LNS paper from the
# anonymized candidate data in ../data/. Requires: pandas, numpy, scipy.
#
#   python reproduce_tables.py
#
# The data files contain only the fields needed to reproduce the published tables.
# The proprietary scoring internals are intentionally not included; `compatibility`
# is the final gated compatibility score S(c,p).

import os
import warnings
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RESULTS = os.path.join(HERE, "..", "results")
os.makedirs(RESULTS, exist_ok=True)

# Published hyperparameters (see paper, Methods)
MIN_SCORE = 0.35     # minimum-score floor
K = 3                # K_max (maximum portfolio size)
COV = ["cov_operational", "cov_decision", "cov_value", "cov_ecosystem",
       "cov_temporal", "cov_change", "cov_capability", "cov_capital"]
NDIM = len(COV)
SECTORS = {"Banking": "banking", "Insurance": "insurance", "Institutional": "institutional"}


def coverage(sub):
    if len(sub) == 0:
        return 0.0
    return sub[COV].astype(bool).any(axis=0).sum() / NDIM


def redundancy_collisions(sub):
    c = 0
    for _, gg in sub.groupby("redundancy_group"):
        c += max(0, len(gg) - int(gg["redundancy_group_limit"].min()))
    return c


def main():
    ablation, per_client, cross = [], [], []
    for name, key in SECTORS.items():
        df = pd.read_csv(os.path.join(DATA, f"{key}_candidates.csv"))
        recs, sizes, comps, covs, sel_clients = [], [], [], [], 0
        for cid, g in df.groupby("client_id"):
            feas = g[(g["feasible"]) & (g["compatibility"] >= MIN_SCORE)]
            mip = g[g["selected"]]
            if len(mip) > 0:
                sel_clients += 1
                sizes.append(len(mip)); comps.append(mip["compatibility"].mean()); covs.append(coverage(mip))
            if len(feas) == 0:
                continue
            greedy = feas.sort_values("compatibility", ascending=False).head(K)
            recs.append(dict(
                mip_cov=coverage(mip), grd_cov=coverage(greedy),
                mip_comp=mip["compatibility"].mean() if len(mip) else np.nan,
                grd_comp=greedy["compatibility"].mean(),
                mip_red=redundancy_collisions(mip), grd_red=redundancy_collisions(greedy)))
        d = pd.DataFrame(recs)
        d = d.dropna(subset=["mip_cov"])
        per_client.append(d)
        try:
            p = wilcoxon(d.mip_cov, d.grd_cov, zero_method="wilcox").pvalue
        except ValueError:
            p = float("nan")
        ablation.append(dict(Sector=name, N=len(d),
                             Cov_MIP=round(d.mip_cov.mean(), 3), Cov_Greedy=round(d.grd_cov.mean(), 3),
                             Comp_MIP=round(d.mip_comp.mean(), 3), Comp_Greedy=round(d.grd_comp.mean(), 3),
                             Redund_MIP=f"{(d.mip_red>0).mean()*100:.0f}%", Redund_Greedy=f"{(d.grd_red>0).mean()*100:.0f}%",
                             Cov_p=round(p, 3)))
        cross.append(dict(Sector=name, Portfolios=sel_clients,
                          Mean_size=round(np.mean(sizes), 2), Mean_compat=round(np.mean(comps), 3),
                          Mean_cov=round(np.mean(covs), 3)))

    allc = pd.concat(per_client)
    try:
        pp = round(wilcoxon(allc.mip_cov, allc.grd_cov, zero_method="wilcox").pvalue, 3)
    except ValueError:
        pp = float("nan")
    ablation.append(dict(Sector="Pooled", N=len(allc),
                         Cov_MIP=round(allc.mip_cov.mean(), 3), Cov_Greedy=round(allc.grd_cov.mean(), 3),
                         Comp_MIP=round(allc.mip_comp.mean(), 3), Comp_Greedy=round(allc.grd_comp.mean(), 3),
                         Redund_MIP=f"{(allc.mip_red>0).mean()*100:.0f}%", Redund_Greedy=f"{(allc.grd_red>0).mean()*100:.0f}%",
                         Cov_p=pp))

    A = pd.DataFrame(ablation)
    totals = pd.read_csv(os.path.join(DATA, "cross_sector_totals.csv"))
    C = pd.DataFrame(cross).merge(
        totals.rename(columns={"sector": "Sector"}).assign(Sector=lambda x: x.Sector.str.capitalize()),
        on="Sector", how="left")[["Sector", "clients", "Portfolios", "success_rate", "Mean_size", "Mean_compat", "Mean_cov"]]

    pd.set_option("display.width", 200)
    print("\n=== Table: optimizer vs greedy top-K (ablation) ===")
    print(A.to_string(index=False))
    print("\n=== Table: cross-sector portfolio generation ===")
    print(C.to_string(index=False))
    A.to_csv(os.path.join(RESULTS, "table_ablation.csv"), index=False)
    C.to_csv(os.path.join(RESULTS, "table_cross_sector.csv"), index=False)
    print(f"\nWrote results/table_ablation.csv and results/table_cross_sector.csv")


if __name__ == "__main__":
    main()
