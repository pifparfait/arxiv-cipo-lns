# CIPO-LNS — Reproducibility Data

Anonymized data and scripts to reproduce the quantitative tables of the paper
**"CIPO-LNS: Context-First Portfolio Recommendation for Cold-Start Intervention Selection"**


This bundle lets anyone regenerate the ablation, cross-sector, and robustness numbers
in the paper. It contains the candidate-level selection data and the derived result
tables. **The proprietary CIPO-LNS engine — context-extraction prompts, the calibrated
ontology, and the internal scoring model — is intentionally not included.** The field
`compatibility` is the final gated compatibility score S(c,p); the engine's internal
sub-scores are excluded.

## Contents

```
cipo-lns-data/
├── README.md
├── LICENSE                     # MIT (scripts). Data under CC BY 4.0 (see below).
├── CITATION.cff                # citation metadata (authorship + version)
├── data/
│   ├── banking_candidates.csv        # per client–product candidate rows
│   ├── insurance_candidates.csv
│   ├── institutional_candidates.csv
│   ├── cross_sector_totals.csv       # client / portfolio counts per sector
│   └── robustness_jaccard.csv        # Jaccard vs full-information portfolio (Test 6A)
├── scripts/
│   └── reproduce_tables.py           # regenerates the tables from data/
└── results/
    ├── table_ablation.csv            # produced by the script
    └── table_cross_sector.csv        # produced by the script
```

## Reproduce

```bash
pip install pandas numpy scipy
python scripts/reproduce_tables.py
```

This prints, and writes to `results/`, the optimizer-vs-greedy ablation table and the
cross-sector generation table. Reported hyperparameters (minimum-score floor 0.35,
maximum portfolio size K = 3) are set as constants at the top of the script.

## Data dictionary (`*_candidates.csv`)

| column | meaning |
|---|---|
| `client_id`, `product_id` | anonymized identifiers |
| `compatibility` | final gated compatibility score S(c,p) ∈ [0,1] |
| `feasible` | passed the hard gates (eligibility / actor / blocking) |
| `selected` | chosen by the CIPO-LNS optimizer (the MIP portfolio) |
| `redundancy_group` | anonymized substitution-group code |
| `group_kind` | `single` / `direct_substitute` / `close_alternatives` |
| `redundancy_group_limit` | max products admissible from the group |
| `cov_*` (×8) | whether the product covers each of the 8 portfolio dimensions |

## Anonymization

All institution names and original product/client names and identifiers have been
removed. Client IDs, product IDs, and redundancy-group names are recoded to opaque,
per-sector codes. Datasets are synthetic; no personal or client-level data are included.

## License

- **Scripts** (`scripts/`): MIT — see `LICENSE`.
- **Data** (`data/`, `results/`): Creative Commons Attribution 4.0 (CC BY 4.0),
  https://creativecommons.org/licenses/by/4.0/ — reuse permitted with attribution.

## Citation

Please cite the paper and this dataset (see `CITATION.cff`). For a permanent, citable
DOI and an authorship timestamp, archive a release of this repository on Zenodo
(https://zenodo.org), which mints a DOI and records the release date.
