# Retained historical sources and decisions

Paths in the accepted tables keep their original spelling. Resolve a
`snapshot_path` beginning `research/` relative to this directory, not relative to
the executable code. `inputs/...` references identify `../normalized/` tables.
URLs and historical handoff locators retain their original provenance meanings.
They are not instructions to fetch or rebuild another project.

The canonical index is `../normalized/evidence_snapshot_links.csv` (1,089 links,
380 distinct SHA-256-verified snapshots). The research register names 296 saved
files supporting accepted findings and explicitly unresolved facts. Current
accepted adjudications are in `../normalized/decisions.csv`, with original
rationale and conflicting raw assertions in the source folders.

Retained classes include pinned cabinet/Atlas compilations and raw assertions;
official appointment and succession acts; parliamentary diaries; dated personal
party observations; TSE registry results and identity disambiguation; party
organization records; source-access limitations; negative searches supporting
continued UNKNOWN states; and accepted date/affiliation/primary-assumption
reviews. A failed retrieval or partial-list absence is never upgraded into a
historical fact. Acquisition snippets document original search scope; they are
not supported reconstruction commands and are never run by the build.

The twelve full parliamentary diaries in
`research/refinement_v5/worker_7_lula_dates/sources/` are retained because their
text layers and selected dispatch pages were actually reviewed in adjudicating
Sabino’s date bounds. Their original hashes are verified against the existing
`diary_review_manifest.json`. Extracts and selected renders do not replace them.
The separately retained 2018 candidate CSV under `processing/` is documentary
support for four inherited affiliation assertions; reconstruction does not read
electoral candidate data to infer a party.

Inherited cross-reference labels resolve as follows; they are not independent
corroborating sources:

| Original label | Local retained record in `research/inherited/` |
| --- | --- |
| CODE-04 | `audit__code_dependency_audit.md`, CODE-04 |
| LEG record for Quintella | `audit__prior_evidence_assertions.csv`, Quintella row |
| MAIN_AUDIT_REPORT.md sections 3,6 | `audit__MAIN_AUDIT_REPORT.md` |
| OCC-005 | `audit__office_audit__occupancy_discrepancies.csv`, OCC-005 |
| OFF-031–OFF-034 | `audit__office_audit__evidence_assertions.csv`, those IDs |
| office_audit/occupancy_discrepancies.csv | `audit__office_audit__occupancy_discrepancies.csv` |
| office_audit/pinned_source_rows.csv | `audit__office_audit__pinned_source_rows.csv` |
| prior_evidence_assertions.csv | `audit__prior_evidence_assertions.csv` |

Original research notes are preserved as evidence, so their descriptions of past
work directories, packages and removed one-time scripts are historical. Current
instructions are in the project README. No retired repair, integration, package
verification or predecessor-release reconstruction is operational.

A distinct `earlier_merge_review.json` from the Temer worker is retained beside
the accepted merge review because the two differ. Its role is historical decision
context; neither is a computational input. Small research records whose unique
supporting role is uncertain remain preserved for later allowlisted review.
