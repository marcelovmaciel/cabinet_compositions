# Read-only code and dependency audit

Audit date: 2026-09-10. Initial release scope: 2015-01-01 through 2026-03-19 inclusive; proposed machine interval `[2015-01-01, 2026-03-20)`. Measurement: parties formally represented by people currently occupying qualifying cabinet offices, using affiliation at the date of service. This is neither appointment origin nor negotiated coalition membership.

All cited repository line numbers describe the paused working tree unless expressly marked `HEAD baseline`. The preserved pre-task status lists `scraping/reconstruct_cabinet_timeline.py` as clean; consequently its `HEAD` content is a legitimate code comparator, while saved pre-task outputs under `/tmp/appointment_time_before/` remain the empirical baseline. Nothing here treats WIP as approved or runnable.

The five required preservation materials were present and inspected, including the relevant code sections of the WIP patch. Fresh `preservation/before.json` was present before source inspection. The separate preservation caveat for `scraping/tests/test_psc_cabinet_chronology.py` is material: its original untracked content was not snapshotted; its current preserved copy is `/tmp/APPOINTMENT_TIME_AFFILIATION_WIP_UNSEPARATED/scraping/tests/test_psc_cabinet_chronology.py`. Neither it nor any repository file was modified by this sub-audit. Root audit performs the final whole-tree comparison.

## Principal implementation findings

1. The baseline is a hybrid, not a validated contemporaneous reconstruction. A single Wikipedia party label is accepted as `high`/`resolved` and extended through the appointment; selected multi-party labels use election records or chronology of party names to infer the starting affiliation; only Gilson Machado has explicit CSV affiliation slices. The WIP replaces this with one frozen affiliation per appointment. Neither is the target object.
2. Office selection has no dated legal-status register. Navigation-box headings are matched to role labels and become an undated administration-level allowlist. A textual prefix supplies `ministerio` versus `orgao_status_ministerial`. Office gaps are mislabeled as known vacancies from absence between scraped rows; unclear dates and missing starts can remove observations without a corresponding unknown-occupancy interval.
3. Raw PR is removed because it equals the lowercase Brazilian state code `pr`. Blank/dash and explicit `sem partido` all yield no party token. These are concrete parsing defects, independent of substantive research outcomes.
4. All source endpoints are treated inclusively. If a source's end date is effective departure and the successor begins that date, the algorithm manufactures a day containing both parties. It also aggregates temporary substitutes and titular incumbents without an adjudicated capacity rule.
5. Stable person, office and party identities are absent; source page/table/row keys are useful locators but change with source layout. Temporal party history is split among Python constants, a two-row affiliation CSV and Julia aliases/lineage. The alias CSV mixes election harmonization and names dated only by year.
6. Current output validates continuous *set intervals*, not full officeholding or affiliation coverage. There is no composition uncertainty model, no record of unspecified alternatives, and no authoritative membership-to-person witness bridge. The WIP instead refuses any unresolved appointment, even one whose ambiguity cannot change the aggregate set.
7. A clean boundary already exists conceptually at the cabinet-to-election crosswalk. Keep reconstruction in standalone Python with reviewed inputs, and keep electionsBR ingestion, crosswalk policy and accounting in Julia. No new ecosystem is needed.

## Actual dependency map

```text
Wikipedia navboxes + role tables
  scrape_wikipedia_orgaos_ministeriais.py
    -> scraping/output/orgaos_ministeriais.json [undated selection input]
Wikipedia pinned revision HTML + cabinet_source_snapshot.json
  reconstruct_cabinet_timeline.py
    -> parse dates / roles / raw party tokens
    -> baseline: single labels + hardcoded start resolutions + Gilson spells
    -> paused WIP: appointment_affiliations.py [frozen; required CSV absent]
    -> clipped appointments + events + party union periods
    -> scraping/output/partidos_por_periodo.{json,csv}
    -> dashboard and source/event/interval CSVs
Processing/src/code.jl + PartyNames.jl + analysis_runner_core.jl
    -> select periods overlapping election mandate
    -> cabinet_to_election_party_crosswalk.csv + election-year aliases
    -> electionsBR votes/seats -> accounting
running/running.jl -> coalesce translated periods -> paper tables/figures
CoalitionDecomposition.jl -> district accounting and decomposition
```

`main()` in reconstruction writes eight output artifacts and invokes appointment construction twice (`scraping/reconstruct_cabinet_timeline.py:1654`). It is unsuitable as an audit diagnostic or standalone data build. `fetch_page_payload()` reads pinned cached HTML but falls back to requests and writes cache files inside `scraping/data/wikipedia_pinned` (`:223`, `:250`). Pinned revision lookup is worth retaining in a separate research importer; a release build must require reviewed local tables and never call it.

## Exact code findings and proposed disposition

| ID | Actual location | What it does; implication | Disposition |
|---|---|---|---|
| CODE-01 | `scraping/scrape_wikipedia_orgaos_ministeriais.py:78`, `:161`, `:215` | Extracts cabinet navbox headers, fuzzy-matches role labels (60% token match at `:154`) and writes the allowlist. No legal-status or effective-date evidence. | Retain only as lead inventory; replace authoritative scope with dated office-status coding. |
| CODE-02 | `scraping/reconstruct_cabinet_timeline.py:164`, `:207`, `:756` | Uses undated allowlist; name prefixes classify status; unmatched offices disappear. | Replace in builder. Research importer should retain excluded/unmatched candidates and reasons. |
| CODE-03 | `:423`, `:454`, `:743`, `:830` | First parsed date populates start/end; header names such as `posse` do not prove underlying event semantics. Multiple dates are marked but not adjudicated. | Keep raw parsing helper in research tooling only; reviewed normalized dates enter deterministic build. |
| CODE-04 | `:464`, `:475`; older scraper `scrape_wikipedia_ministerios.py:285`, `:335` | PR is discarded as UF; empty/dash and explicit no party yield equivalent empty token lists. | Do not use token absence to code status. Keep PR lexical fixture; preserve raw text. |
| CODE-05 | `HEAD baseline reconstruct_cabinet_timeline.py:648`, `:670`; WIP patch `:2885`–`:2982` | `resolve_start_party` labels one raw party resolved/high; overrides use 2018 candidate affiliation for later dates; Anderson PSL follows impossibility of later UNIÃO label, not personal evidence. | Retire as historical coding authority; reuse observations only as evidence leads. |
| CODE-06 | `HEAD baseline :601`, `:1235`; `scraping/data/cabinet_party_affiliation_spells.csv` | Gilson-only affiliation slices also change appointment end, require every party to occur in raw candidate labels, and embed person-specific note. | Separate officeholding decisions from personal affiliation; preserve source assertions, reassess boundary. Never constrain supported parties to Wikipedia labels. |
| CODE-07 | paused `:1046`, `:1205`; `scraping/appointment_affiliations.py:19`, `:51` | Explicitly ignores in-tenure switching and merger effects. Required `scraping/data/cabinet_appointment_affiliations.csv` does not exist. | Do not resume; preserve WIP. Borrow required-field/duplicate/stale-evidence validation patterns, not frozen semantics. |
| CODE-08 | `:1067`, `:1069`, `:1073`, `:1089` | Missing start and multiple-date records can be skipped; source/page windows clip occupancy; literal non-entry flag removes service. | Record entry/non-entry/unknown explicitly; unknown occupancy must survive filtering. Dates require documentary decisions. |
| CODE-09 | `:555`, `:566`, `:1092` | Classifies interim/substitute/secretary by text, then treats all surviving capacities as party witnesses. | Reviewed capacity and whether titular retains office become inputs. Count vacancy holder; do not add temporary delegate during continuing titular spell. |
| CODE-10 | `:849`, `:911`, `:1029` | Orders records by ministry text; gaps between adjacent rows generate vacancy with `needs_review=False`. | Retain gap detector as warning; use unknown occupancy unless documented vacancy. Dated office IDs prevent false continuity through reorganizations. |
| CODE-11 | `:1211`, `:1239`, `:1253` | Inclusive end, next-day removal; set union uses `Counter`, so last representative logic and same-party personnel coalescing are structurally sound when inputs are valid. | Retain boundary sweep idea, rewrite half-open intersections and include affiliation/office status/organizational/uncertainty boundaries. |
| CODE-12 | `:1258`, `:1266`, `:1284` | Coalesces solely on party string list, may cross administration boundaries while retaining starting `government_id`; checks output dates but not office census. Empty complete party set raises at `:1257`. | Explicit reporting-boundary convention; stable IDs; permit verified empty set if all offices known vacant or unaffiliated. Separate three completeness dimensions. |
| CODE-13 | `:1302`, `:1333`, `:1477` | JSON/long CSV party outputs useful for exchange, but IDs are year sequence and membership has no witness foreign keys. People and office labels serve as identity. | Versioned period IDs and party-ID rows; separate witnesses to intersections and evidence. Keep labels display-only. |
| CODE-14 | `Processing/src/PartyNames.jl:125`, `:170`, `:219`, `:305`; `data/party_aliases.csv` | Generic canonicalization falls back to unfiltered alias candidates if no year candidate (`:145`); strict date path uses only calendar year; fusion function handles only first matching fusion, not general org history; WIP appointment path ignores date entirely. | Lexical normalizer `:113` can stay in consumer. New cabinet registry uses dated attributes/stable IDs and explicit org events; no importing Julia. |
| CODE-15 | `Processing/src/code.jl:1030`, `:1054`, `:1099`; `running/running.jl:1240`, `:1381`, `:1424` | Loads raw cabinet lists, selects electoral windows, translates one-to-many with same-label fallback, sums accounting. Translation duplicated in runner. | New release reader plus one consumer adapter; retain mapping/report semantics but remove label-based identity inference. Explicit unmapped/non-additive status. |
| CODE-16 | `Processing/src/cabinet_period_coalescing.jl:13`; `analysis_runner_core.jl:48`, `:84`; `CoalitionDecomposition.jl:403` | Coalesces election-specific party sets; uses inclusive duration; later decomposition consumes metrics. | Keep as consumer-only reporting transformation with source dataset IDs retained. Derive cabinet periods first; never feed election equivalence back into cabinet data. |

### What is reusable from previous appointment work

Person-specific dated observations, source URLs, pinned revisions, original source text, appointment/date identity checks, duplicate rejection, and explicit UNAFFILIATED versus missing are useful research material. A point observation can seed a continuity spell under the stated persistence-and-search convention. The dates and conflicts must be recoded as assertion-level evidence rather than flattened `evidence_source` and semicolon-separated dates. No separate daily citation is required.

The frozen continuation, retention of predecessor identities after merger, rejection of all individual uncertainty, confidence labels as certification, preserved old-assignment fallback, and fixed appointment population are not transferable. The old Gilson CSV's temporal slicing idea is transferable; its March 30 membership/officeholding overlap is a documentary boundary question, not a pre-approved fact. The saved baseline and conditional outputs remain comparison material only.

## Existing tests: retain, adapt, archive

No existing suite was run. Some fixtures are empirical expectations tied to old headline results; passing them would not establish the new measurement.

| Test location | Useful behavior | Required treatment |
|---|---|---|
| `scraping/tests/test_appointment_affiliations.py:40`, `:45`, `:59`, `:78`, `:94` | No backprojection, missing versus unaffiliated, stale keys, no party contribution, coalescing, no silent unknown omission. | Adapt to dated spells and aggregate uncertainty; incomplete data can produce explicit incomplete output, while verified export rejects undetermined membership. |
| Same file `:65`, `:88`, `:112`, `:120`, `:127` | Enforces frozen switching, no merger, whole-tenure named people and inclusive period assumptions. | Archive as appointment-model tests; do not port expected behavior. Replace with contemporaneous change and boundary fixtures. |
| Same file `:100`, `:134` | Loads required affiliation file, extracts source records and compares generated products. | Missing CSV makes paused integration incomplete; live scrape/cache fallback unsuitable. Replace with pinned reviewed fixture build plus byte reproducibility. |
| `scraping/tests/test_psc_cabinet_chronology.py:11` | Frozen PSC throughout Gilson tenure. | Preserve current and separately preserved copy; no inferred original delta. Future documented chronology fixture only after boundary adjudication. |
| `Processing/test/test_cabinet_period_coalescing.jl:8` | Order-insensitive party sets, no gap bridging, no election-window merging, value consistency, provenance. | Retain in consumer; add half-open contract conversion test and distinguish historical versus translated coalescing. |
| Same file `:48` onward | Hardcodes period counts, dates, inversion count, duration and quantities. | Keep only as archived release regression, not acceptance criteria for a corrected dataset. |
| `Processing/test/test_coalition_period_linkage.jl:31` | Select by overlap, not period label year. | Retain principle with synthetic IDs, explicit half-open date conversion and pinned release metadata; retire fixed historical IDs as universal truths. |
| `Processing/test/test_coalition_strict.jl:23` | Unknown/ambiguous alias and missing/duplicate electoral-party errors. | Retain electoral accounting checks; replace cabinet label mapping with stable identity crosswalk. |
| `Processing/test/test_party_name_drift.jl:104`, `:144`, `:152` | Context-sensitive alias handling; snapshots. | Keep election spelling tests. Cabinet snapshot tests become version-specific approved release checks. |
| `Processing/test/test_psc_baseline_repair.jl:24`, `:103` | Election candidate-status checks; specific cabinet PSC periods. | Keep electionsBR correctness in consumer; split cabinet historical assertions from electoral totals and recertify only after evidence review. |
| `Processing/decomposition/test_decomposition.jl`, `test_accounting_integration.jl`, `test_intermediate_accounting_report.jl` | Downstream accounting consistency. | Keep with consumer; not evidence or reconstruction tests. Review sample-specific expected cabinet cases only when a release is authorized for consumption. |

New fixtures/invariants belong in the main audit test specification; do not require fixed counts of appointments, compositions, inversions, or figures.

## Dependencies and execution safety

Python reconstruction imports `requests` and `bs4`; `scraping/requirements.txt` declares only `requests>=2.0` and `beautifulsoup4>=4.12`. Deterministic construction from CSV/JSON/ISO dates can use existing Python standard-library `csv`, `json`, `datetime`, `collections`, `hashlib`, `argparse`, and `unittest`. Acquisition can retain requests/BeautifulSoup separately. No pandas, database, service, package framework or temporal engine is required.

The Julia project already includes CSV, DataFrames, Dates, JSON and JSON3 (plus existing visualization/analysis dependencies); keep them in the consumer. A movable cabinet directory must not import Processing, electionsBR, manuscript writers or global repo paths. The design does not request dependency changes.

`scratch_code_diagnostics.py` AST-selects pure functions, supplies controlled globals and uses explicitly fictional three-day inputs. It never imports a production module and makes no network calls. Its JSON shows literal `PR -> []` and a same-day inclusive succession producing `A -> {A,B} -> B`. The proposed half-open expectation is valid only if the source end is an effective departure; the diagnostic does not adjudicate real dates. It also verifies the paused required CSV is absent. Script and output are entirely in this audit directory, with explicit fictional coverage and no empirical completeness claim.
