# Cabinet Compositions

This repository reconstructs the composition of Brazilian federal cabinets from
January 2015 through March 19, 2026, with particular attention to the set of
political parties represented in qualifying cabinet offices over time.

This repository owns the cabinet-data construction and validation pipeline
and publishes the release consumed by
[`coalition_inversions`](https://github.com/marcelovmaciel/coalition_inversions).
The substantive coalition-inversion analysis and paper replication workflow
belong to that downstream repository.

Qualifying officeholding is dated separately from personal party affiliation.
The cabinet party set is the set of parties represented by qualifying
officeholders on each date. Appointments, departures, affiliation changes,
party organizational changes, vacancies, uncertainty, and provisional cases
are represented explicitly. `UNKNOWN` affiliation remains distinct from
unaffiliated status.

## Data and evidence

`data/normalized/` contains the structured inputs used for reconstruction.
`data/source/` contains retained historical evidence and source snapshots; its
[source guide](data/source/README.md) describes the collection. The relevant
party projection and crosswalk material is in `data/projection/`.

The coding rules are documented in [CODEBOOK.md](CODEBOOK.md), and the
published release schema is documented in [CONTRACT.md](CONTRACT.md).
Historical uncertainty and provisional coverage remain explicit in the inputs
and outputs.

## Building the reconstruction

The runtime uses Python 3.11 or newer and the standard library, as specified in
[environment.toml](environment.toml). Git LFS is required for the retained
source PDFs. Run these commands from the repository root:

```bash
python3 -B scripts/build_release.py --output build/reconstructed
python3 -B scripts/validate_release.py --build build/reconstructed
make test
```

The first command builds a fresh reconstruction under `build/reconstructed`.
The second validates that build and compares its release files with the
published release. `make test` runs the repository test suite and creates its
own temporary reconstruction.

## Published release

The current release is
[releases/2026-03-19-v6-election-v1/](releases/2026-03-19-v6-election-v1/).
Together, these four files form the compact published representation of the
reconstructed cabinet party-set history:

| File | Contents |
| --- | --- |
| `cabinet_periods.csv` | Primary party sets and their date intervals. |
| `cabinet_sensitivity_periods.csv` | Alternative calendars for coded uncertainties. |
| `cabinet_coverage.csv` | Administration and established or provisional coverage by date. |
| `metadata.json` | Release identity, conventions, scenarios, and checksums. |

## Historical documentation

[CABINET_HISTORY_AUDIT.md](docs/CABINET_HISTORY_AUDIT.md) is a source-linked
chronology and audit. [CABINET_HISTORY_NARRATIVE.md](docs/CABINET_HISTORY_NARRATIVE.md)
is a readable prose history of the cabinet composition changes.
