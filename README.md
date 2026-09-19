# Cabinet Compositions

This repository constructs the cabinet-party composition data used by the
coalition-inversions analysis. It combines appointment and service information,
party-affiliation evidence, accepted adjudications, and uncertainty and
sensitivity coding to produce Brazil's cabinet calendars from January 2015
through March 19, 2026.

## Data and evidence

Reviewed service, affiliation, and adjudication tables are retained in
`data/normalized/`. Supporting documents, source snapshots, and research records
are kept in `data/source/`; its [source guide](data/source/README.md) explains
the material. The election-year party crosswalk is in `data/projection/`.

Reconstruction starts from the reviewed inputs. Historical research and decisions
about conflicting sources are recorded alongside them, rather than repeated by
the build. Unresolved affiliation and date uncertainty remain explicit in the
data. Provisional coverage and alternative calendars show where results depend
on assumptions; unknown affiliation is not silently treated as non-affiliation.
See [CODEBOOK.md](CODEBOOK.md) for the coding rules.

Read the [cabinet history narrative](docs/CABINET_HISTORY_NARRATIVE.md) for the
evolution of party composition, or consult the [chronological evidence audit](docs/CABINET_HISTORY_AUDIT.md)
for individual events, source links, coding decisions, and retained uncertainties.

## Building the release

Use Python and its standard library; the supported version is recorded in
[environment.toml](environment.toml). Git LFS is needed to retrieve the large
source PDFs. Run these commands from the repository root:

```bash
python3 -B scripts/build_release.py --output build/reconstructed
python3 -B scripts/validate_release.py --build build/reconstructed
make test
```

The first command builds the cabinet chronology and exports the calendars to
`build/reconstructed/release/`. Choose a new directory under `build/` for each
reconstruction; the command refuses to overwrite an existing destination.

The second command checks the evidence, calendar consistency, and agreement with
the published release. `make test` runs the scientific tests and makes its own
fresh reconstruction, so it can also be run on its own. Set `PYTHON_BIN` for
`make test` if your Python executable has a different name or location.

Generated files stay under the Git-ignored `build/` directory. Building a release
does not replace the published dataset.

## Published release

The current dataset is in
[releases/2026-03-19-v6-election-v1/](releases/2026-03-19-v6-election-v1/).
Downstream users need these four files together:

| File | Contents |
| --- | --- |
| `cabinet_periods.csv` | Primary cabinet party sets and their date intervals. |
| `cabinet_sensitivity_periods.csv` | Complete alternative calendars for the coded uncertainties. |
| `cabinet_coverage.csv` | Administration and established or provisional coverage by date. |
| `metadata.json` | Release identity, conventions, scenario definitions, and checksums. |

Party sets are already projected to election-year party identities here.
Downstream users do not need to reconstruct historical affiliation or apply the
party crosswalk themselves. [CONTRACT.md](CONTRACT.md) describes the fields and
date conventions.

## Relationship to coalition_inversions

This repository produces the cabinet dataset. `coalition_inversions` consumes a
pinned copy of the published release to calculate electoral outcomes; its analysis
does not call the cabinet reconstruction code.
