# Cabinet election-calendar contract, schema 1

The public dataset is explicitly selected as
`releases/2026-03-19-v6-election-v1/`. Its complete interface consists of
`cabinet_periods.csv`, `cabinet_sensitivity_periods.csv`, `cabinet_coverage.csv`
and `metadata.json`. Select that directory by exact path and check the metadata
release/schema versions; never discover the newest directory. Consumers need
only these four ordinary UTF-8 files, with no producer imports or other reads.
This codebook and all reconstruction/projection inputs remain producer-side.

Reconstruct and validate from the producer root:

```bash
python3 -B scripts/build_release.py --output build/reconstructed
python3 -B scripts/validate_release.py --build build/reconstructed
```

The exporter uses the fresh `historical/` construction under that build and
writes its four-file `release/`. Existing outputs and destinations outside
`build/` are rejected. The standard-library implementation constructs complete
alternatives from witnesses and coupled constraints, projects complete party
sets to election identities, then recompresses. It reads no election vectors,
ideological order, coalition accounting or manuscript.

The crosswalk and scientific pins reside in `data/projection/`. The original
source-metadata digest and source/projection locators in the public metadata are
unchanged historical provenance; they do not require a stored predecessor
release or a retired filesystem layout. The current builder is validated using
39 exact scientific/evidence table hashes, then the four public files are
compared byte-for-byte. Changing the code does not falsify its own metadata hash.

## Tables and fields

| File | Exact ordered fields | Consumer reason |
| --- | --- | --- |
| `cabinet_periods.csv` | `period_id,election_year,start_inclusive,end_exclusive,party_set` | Identify primary periods, join the correct election vector, recover actual appearances and day weights, and calculate electoral results from complete membership. |
| `cabinet_sensitivity_periods.csv` | `scenario_id,period_id,election_year,start_inclusive,end_exclusive,party_set` | Repeat the same calculations for each complete finite alternative timeline. |
| `cabinet_coverage.csv` | `start_inclusive,end_exclusive,administration,status` | Join administration and exact established/provisional date masks independently of maximal membership periods, including exclusion calculations. |

All dates use ISO `YYYY-MM-DD`, inclusive start and exclusive end, with the
accepted closing-state convention. Duration is the calendar-date difference;
`days` and daily records are deliberately not duplicated. Coverage is continuous
from 2015-01-01 through 2026-03-20 exclusive. Metadata defines the 2014, 2018 and
2022 election windows. Every timeline covers that entire calendar once.

`party_set` is a sorted, unique, semicolon-separated list of election-year party
labels. An empty field means a **complete empty set**. A missing cell/row is
invalid, and unbounded unknown is never encoded as an empty set or invented
party. An unchanged scenario interval explicitly repeats primary membership;
there is no implicit patch or inheritance of membership. Recurrent sets retain
separate appearances. Parties produced by one-to-many merger mappings are
unioned before compression, so there is no double counting.

`period_id` is the accepted `CV5-NNN` chronological identifier, scoped to the
primary calendar or to `scenario_id`. A boundary is created only by an election
or translated membership change. Periods may cross administration or status
boundaries: intersect with the separate coverage intervals. Derive annual period
display labels by numbering period starts within each calendar year. Group
canonical `(election_year,party_set)` values downstream to construct distinct set
identifiers; add the durations of actual occurrences, never their first-to-last
span. Cabinet-derived quantities, inversion flags and electoral conclusions are
not part of this dataset.

## Sensitivities and uncertainty

Metadata gives each scenario's opaque stable `scenario_id`, grouping
`sensitivity_id`, `kind`, `candidate`, half-open affected scope, meaning and
`unbounded_personal_uncertainty` flag. Identifiers retain their accepted legacy
spelling for exact comparison; consumers must not parse historical details from
them. Candidate affiliation labels are also opaque upstream labels: the table's
complete election-year party sets, not candidate names, determine membership.

All 52 accepted finite alternatives are separate complete calendars, including
alternatives with no aggregate membership change. These are **one-at-a-time**
scenarios: candidates within a sensitivity group are mutually exclusive. No
cross-group joint scenarios or exhaustive joint uncertainty are claimed. Coupled
service starts/ends and adjacent affiliation states move together upstream;
removing a changed witness preserves any independent witness for its party.

Coverage status is `established` or `provisional`, and all finite calendars retain
the accepted primary status mask. Provisional means the primary assumes no
additional party contribution from unresolved affiliation, not established
historical unaffiliation. Metadata marks those exact provisional scopes as
`unbounded_unknown`. The finite MRE entry alternative additionally retains its
unbounded-personal-uncertainty flag. Its calendar remains conditional on the
primary assumption; no finite enumeration resolves that uncertainty or proves
that other electoral effects are impossible.

Metadata also provides schema/release version, exact table columns, election
windows, conventions, coding policy and the producer-side provenance locator
with the pinned source metadata and projection checksums. These locators are
informational: the consumer need not open them. One SHA-256 checksum pins the
three CSVs, framed in lexical filename order as UTF-8 filename, NUL, exact bytes,
NUL. No source/evidence manifest, historical identity crosswalk or evidence file
is part of the public interface.

The validation command runs all scientific tests, including the independent
`tests/test_data_contract.py` reader on the freshly generated four files. It
checks complete calendars, scenario scopes, the separate status mask, schema and
checksum without importing producer construction code. The coalition consumer
uses its own pinned copy and independent contract reader.
