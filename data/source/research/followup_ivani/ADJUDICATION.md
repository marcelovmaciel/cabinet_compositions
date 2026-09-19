# Ivani dos Santos affiliation follow-up

Research date: 2026-09-10/11. Person: `person-ivani-dos-santos`. Existing case: `C035`.

**Result: personal affiliation remains unresolved.** No examined source establishes that this officeholder was personally affiliated to a party, or explicitly unaffiliated, during the three qualifying vacancy replacements. This follow-up does not authorize changing an UNKNOWN row to PMDB or non-affiliation. It also does not establish a finite, exhaustive PMDB/non-affiliation alternative set. No canonical input, builder, or release was changed by this follow-up.

The affected half-open spells are `[2016-11-25,2017-02-03)`, `[2017-08-02,2017-08-03)`, and `[2017-10-20,2017-10-26)`: 70, 1, and 6 days respectively, totaling **77 days**. These are genuine vacancy replacements under the adopted scope, not ordinary leave substitutions. Continuing employment as executive secretary outside these spells does not make all of that employment qualifying ministerial service.

## Identity and office evidence

The Presidency's institutional history identifies the substitute as Ivani dos Santos, born in Anápolis-GO in 1952. Câmara employment records identify Ivani dos Santos as career employee point number 1920, serving PMDB leadership offices in 1992 and 2013. This supplies an identity trail and establishes the nature of her long PMDB association. It does not establish membership in that party. A later parliamentary retirement record likewise concerns civil-service status, not affiliation or the end of commissioned ministerial service.

Official succession evidence and contemporary reporting already support the three service intervals in case C035. The new searches found no basis for removing those intervals from the cabinet scope.

## Affiliation evidence actually found

Contemporary accounts consistently describe her employment under Geddel Vieira Lima and the PMDB leadership. In January 2017 PMDB politicians wanted her retained when Imbassahy took over. December reporting again groups her among trusted PMDB-associated staff. These accounts establish a professional and sponsorship relationship. None calls her a party member or explicitly unaffiliated.

The TSE's PMDB 2014 annual-account annex 15 contains a memo signed by Ivani as chief of cabinet requesting printer cartridges for the parliamentary leadership. It is not a membership certificate, membership list, or dues payment. A PPS 2011 account search result contains the exact same name in a dues context, but the identifying number differs from the official officeholder record: this is a homonym and was not adopted. Ivany Guilherme dos Santos in a PMDB women's record is also a different name, not evidence about the minister.

The supplied raw Atlas file `atlas/7010-261partidogabineteministerio.csv` contains no Ivani/Ivany row. The pinned Temer Wikipedia roster likewise moves directly from Geddel to Imbassahy to Marun and omits her. The current Secretariat's Wikipedia list does so too. These omissions establish neither affiliation nor non-affiliation; they cannot supply a personal party label.

## Public TSE registry search

A newly accessible public TSE endpoint permits party-by-municipality queries. `scan_tse_go.py` queried every one of the 39 party identifiers supplied by its metadata for Anápolis and Goiânia, the two plausible Goiás municipalities selected from the institutional identity trail. All 78 queries succeeded. They examined 123,748 records and found no exact normalized `IVANI DOS SANTOS` or `IVANY DOS SANTOS` match. The parallel DF scan in `../followup_bolsonaro_affiliations/` also found no match.

These are current public records. The public relation does not preserve a complete historical list of cancelled affiliations; its coverage is governed by the current official/public list convention. A missing person is therefore **not evidence of non-affiliation in 2016–2017**, and the Goiás search is not a nationwide exhaustive name search. The machine-readable scan summary states this limit. Raw per-query logs retain response hashes, URL, retrieval time, and counts, with no unrelated people's identifying records retained.

Reproduce the Goiás search from the repository root with:

```sh
python3 cabinet_dataset/research/followup_ivani/scan_tse_go.py
```

The script reads `../followup_bolsonaro_affiliations/tse_partidos.json`; that metadata is part of the same cabinet research tree. Re-running queries will observe the registry at the new retrieval date, not reproduce a historical snapshot. The saved 78 query logs and `tse_go_scan_summary.json` preserve this research run.

## Historical registry access attempted

Historical TSE PMDB/MDB DF and GO bulk URLs returned 403 or 404. Brasil.IO describes a 2018-04-27 affiliation snapshot, with joining and cancellation fields, but the filtered table redirected to login and its linked Google Drive download required authentication. Guessed direct data paths did not recover it. Base dos Dados storage discovery did not locate a public affiliation extract: relevant buckets require requester-pays billing or authentication. An indexed Git mirror's affiliation path was unavailable. Wayback attempts yielded a timeout or no applicable capture. The corresponding retrieval logs distinguish an inaccessible source from a source examined with no matching record.

Other follow-up routes included parliamentary honors/career records, party directories and conventions, women's secretariat appointment reporting, ministerial biographies, contemporary cabinet lists, and targeted Portuguese searches for affiliation, non-affiliation, departures and party membership. They did not yield the missing personal observation. The earlier completion research register and retained web sources remain additional evidence of the investigation already performed; this directory supplements them.

## Exact remaining dependency

A temporally relevant personal affiliation or explicit non-affiliation observation for this identified officeholder is still needed, either during the service window or a credible retrospective statement describing it. A positive historical TSE record could also supply that fact if identity and event dates match. The existing record of PMDB employment cannot make the universe of personal affiliation alternatives exhaustive. Consequently party-set neutrality has not been established for these three spells, despite other certain PMDB ministers being present. The blocker is historical evidence, not a file-hash discrepancy or software failure.

`source_findings.csv` records the principal sources and their actual implications. `remaining_dependency.csv` gives the three exact dependencies for integration into the unresolved-interval accounting.
