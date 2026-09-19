# Cabinet compositions

Offline production of Brazil’s accepted cabinet membership calendar for
2015-01-01 through 2026-03-19. The published interface is the immutable four-file
[2026-03-19-v6-election-v1 release](releases/2026-03-19-v6-election-v1/).
No electoral votes, seats, ideology, manuscript, sibling project or network
service is needed to reconstruct it.

## Reconstruct and validate

Use Python 3.11+ and the standard library; the existing CPython 3.12.1 environment
is verified. [environment.toml](environment.toml) records this requirement.
From this project directory:

```bash
python3 -B scripts/build_release.py --output build/reconstructed
python3 -B scripts/validate_release.py --build build/reconstructed
make test
```

Choose a **new** output directory each time. The first command validates retained
evidence, builds the historical chronology and exports the public calendars. It
stages the entire result, validates construction, and renames the completed
directory atomically. Failure removes its temporary staging directory. Generated
files are restricted to `build/`; source tables, evidence and published releases
are never overwritten. A complete run contains `historical/` (regenerable
construction/diagnostic tables) and `release/` (exactly the four public files).
`build/` is ignored and disposable.

The second command verifies evidence references and hashes, primary coverage,
witness intersections and office accounting; compares all four fresh public
files **byte-for-byte**, including metadata, with the publication; and validates reconstruction. Run `make test` for the independent scientific
suite; it reconstructs its own fresh release once and compares a reordered-input
rebuild, without any pre-existing generated files. The tests cover all 52 complete
sensitivity calendars, 4,096 primary dates, 212,992 scenario dates, and the exact
3,996 established / 100 provisional status mask. It imports no sibling code.

Publication is deliberate: review a completed staging export and select a new
version directory if publishing a different dataset. These commands do not
replace an existing published version. Transferring the four reviewed files to a
consumer and changing that consumer’s pin is a separate explicit operation.
Reconstruction never updates the snapshot in `coalition_inversions`.

## Inputs and construction

| Location | Responsibility |
| --- | --- |
| `data/normalized/` | 24 accepted input tables: qualifying services, dated affiliations, identities, offices, evidence, adjudications, explicit assumptions, bounded constraints and source reconciliation. |
| `data/source/` | Original source snapshots, raw assertions, accepted research/merge decisions and acquisition-method records. See its [source guide](data/source/README.md). |
| `data/projection/` | Accepted election-year crosswalk and scientific reference pins. |
| `src/build.py` | Intersect each qualifying service with the person’s contemporaneous affiliation; retain dated witnesses and coalesce historical membership periods. |
| `src/release_outputs.py` | Coverage, office accounting, transitions, residual uncertainty, bounded-date diagnostics and source-roster reconciliation. |
| `src/export.py` | Construct complete finite alternatives, project to election-year parties, take set unions and maximally compress calendars. |
| `src/validate.py`, `tests/` | Scientific invariants, source integrity, historical regressions and exact release reconstruction. |

Reconstruction starts at the **reviewed, adjudicated input level**. Acquiring
historical documents and adjudicating their claims are not automatic steps.
`decisions.csv` retains 154 accepted decisions; `evidence.csv` retains 745 records,
and `evidence_snapshot_links.csv` resolves 1,089 links to 380 hashed snapshots.
The research register preserves the supporting searches and their limitations.
Source evidence is retained even when a normalized table repeats its information.

The historical object is formal **personal affiliation during qualifying
service**, not portfolio sponsorship. Dates are half-open closing states;
ordinary delegation does not displace an incumbent. Renames preserve identity,
while mergers act only on continuing affiliations. A second minister can preserve
a party in the cabinet after another leaves. Read [CODEBOOK.md](CODEBOOK.md) for
coding rules and [CONTRACT.md](CONTRACT.md) for the exported schema.

Unknown affiliation remains `UNKNOWN`. Twelve authorized assumptions contribute
no additional party on 100 dates involving nine people, without establishing
historical non-affiliation. The 52 finite scenarios vary one accepted uncertainty
at a time, including coupled service/affiliation boundaries. They retain the
primary status mask and do not exhaust unbounded uncertainty.

No predecessor release is a construction input. Historical version names in
stable identifiers and the public metadata remain unchanged for reproducibility.
Its original metadata digest and provenance/projection locators identify the
accepted source release; they are historical identifiers, not live filesystem
requirements. Current construction metadata truthfully records the current code,
input hashes and generated files. The public four-file release is reproduced
without any metadata exception or final-output override.
