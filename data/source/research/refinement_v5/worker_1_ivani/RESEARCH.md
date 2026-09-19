# Ivani dos Santos — v5 focused research

Research date: 2026-09-10 in Brasília/Recife; machine retrieval logs use UTC and therefore show 2026-09-11. Assigned dependency: `person-ivani-dos-santos`, Secretaria de Governo, Temer.

Result: **0 days resolved; all 77 remain UNKNOWN**. No defensible personal party-state correction or finite exhaustive alternative set was found. This is a completed focused research implementation with new source/provenance rows, not a completed historical affiliation determination.

## Prior work read first

The relevant v4 completion blockers, baseline research-register row, all three affiliation and service rows, C035 evidence/decision, residual-person uncertainty, date-sensitivity tables, constraints and CODEBOOK were read before new searches. All 36 files referenced by the Ivani register were loaded in full, along with the 18 retained `ivani_web_*` and `news_*` follow-up files. `prior_inventory.csv` records hashes and the target-containing source-block inventory of those 54 files. Relevant complete source blocks were reviewed after eliminating repeated URLs and separating mixed-person search hits. The earlier `ADJUDICATION.md`, `source_findings.csv`, identity-homonym check, archive retrieval logs, GO scan summary and historical Brasília snapshot findings were also read. No canonical or previous-release file was changed.

Established facts were retained: the officeholder is the Câmara employee numbered 1920, born in Anápolis in 1952; personal identity, employment and the three genuine vacancy substitutions are established. Thirty years of service to PMDB leaders is employment evidence. Longer names, other exact-name registrants whose identifying records differ, and partial-list negatives are not personal affiliation evidence. Prior PMDB party-account material is a printer-cartridge request, not a dues/member record. Re-searches that merely returned those facts were not treated as new corroboration.

## New primary historical channel: SGIP3 governing bodies

Official entry point: https://www.tse.jus.br/partidos/partidos-registrados-no-tse/informacoes-partidarias . The publicly accessible application at https://sgip3.tse.jus.br/sgip3-consulta/ exposes historical governing-body queries, separately from ordinary Filia affiliate lists. The official application JavaScript was inspected to establish its actual public parameters and checkbox semantics; no credentials or undocumented private service were used.

Queries used party number 15, `isComposicoesHistoricas=true`, `dataInicioVigencia=01/01/2016`, `dataFimVigencia=31/12/2017`, and scope codes 81 (national), 82 with GO, and 84 with DF. A preliminary DF query with 82 returned an empty list because DF uses scope 84; that empty response is retained and is not used as an evidentiary negative.

The returned bodies were then read using `api/v1/orgaoPartidario/comAnotacoesEMembros`, their returned IDs, and `isMembrosAtivos=false` (the active-members-only checkbox is not selected). All returned member rows were searched for IVANI or IVANY, which includes both requested full-name variants. No such name occurred.

| Returned organ ID | Governing body | Stated validity | Returned member entries | Hits |
|---|---|---|---:|---:|
| 70945 | National executive commission | 2013-03-11 to 2019-10-06 | 36 | 0 |
| 70946 | National definitive body | 2013-03-11 to 2019-10-06 | 219 | 0 |
| 100311 | Goiás definitive body | 2016-02-05 to 2019-01-18 | 149 | 0 |
| 94158 | Distrito Federal regional definitive body | 2015-10-31 to 2019-05-31 | 127 | 0 |

The 531 entries are returned governing-member rows, not 531 unique persons and not an exhaustive list of party affiliates. The application itself warns that bodies before May 2017 may require a separate historical database. Bodies returned with earlier validity dates cannot establish complete earlier member histories. Consequently this new primary channel supplies neither positive identity evidence nor a valid non-affiliation conclusion. Retained scoped snapshots include response URL, UTC retrieval time, HTTP status, response hash, returned-member count and target matches, while unrelated individuals' identity/contact records were processed transiently and discarded. Evidence: `V5W1E001`.

## New firsthand narrative channel

An exact-name March 2006 UniCEUB monograph, *A Psicologia Cognitiva e a Ética na Política: o cidadão do século XXI e o exercício da cidadania*, was found in the institution's repository. The autobiographical introduction describes its author as a federal legislative employee for 28 years. This is compatible with the known officeholder's career, but does not uniquely establish that identity. Acknowledgements and the introduction contain no personal party-state observation. Targeted full-document indexed searches did not find an affiliation declaration; the PMDB term hit concerns named deputies in an appended ethics code, not the author. No political opinion or academic subject matter was used to infer affiliation.

Repository: https://repositorio.uniceub.br/jspui/handle/235/10435 . Web extraction of the 168-page PDF was accessible; the direct byte request returned HTTP 410. `search_02.json` retains the examined opening and autobiographical passages; `search_03.json` retains the term-search results. The HTTP 410 body is named accordingly, not passed off as a PDF. Evidence: `V5W1E003`.

## Registry-history semantics and additional archive routes

The official TRE-TO Filiaweb operations guide distinguishes internal, official and excluded records, describes an elector's complete record history, and explains delayed processing of changes in the historical system. The TSE external-user manual documents an authenticated history query for a specified elector/party/time range. Those source semantics do not establish that a current public list or the July 2016 municipal mirror is exhaustive over every possible affiliation on the service dates. The SGIP exact-person participation form separately requires name, voter registration and CPF; no verified voter registration was available. No fabricated identity inputs or access bypass was attempted. Evidence: `V5W1E002`.

A new publicly downloadable researcher archive was identified at https://github.com/gabrielcaseiro/tse_filiados . Its checked-in collection script obtains the current Filia consultation lists by municipality, electoral zone and party, paginating them and retaining RDS output. The DF output's Git history is an initial commit dated 2024-07-31. This provides a useful archive lead but no documented exhaustive 2016–2017 event history. Its README, code, output listing and commit metadata are retained. The 475 MB of member data was not downloaded or represented as searched; no person-level result is claimed from it.

The current Perfil Político interface was inspected: its exposed page routes concern candidates by election year, locality and office. This did not supply a public exact-person historical affiliation query for a noncandidate. The current interface and app bundle are retained, with no claim of a complete search of its underlying historical data.

Narrow queries against party websites and ethics/governance terms produced the already known employment reporting, unrelated longer names, or the new academic lead. `search_01.json` through `search_09.json` retain discoveries and limitations. No absence from a website search was used as affiliation evidence.

## Implementation and integration

`merge.json` contains only five changed input files: three affiliation provenance/support updates, one research-register update, three new evidence rows, one new decision, and 18 new snapshot links. States, dates, services, parties and sensitivity constraints remain unchanged. `V5W1D001` explicitly retains UNKNOWN and the full unresolved universe rather than asserting an unsupported PMDB/UNAFFILIATED pair.

Snapshot paths are relative to `cabinet_dataset`: `research/refinement_v5/worker_1_ivani/...`. `snapshot_merge_map.json` maps each isolated source/document to its final canonical research destination. The root should merge the upserts and copy the mapped snapshots before packaging.

Required isolated command was run:

`python3 cabinet_dataset/refinement_v5/baseline/build.py --inputs cabinet_dataset/refinement_v5/worker_1_ivani/inputs --output cabinet_dataset/refinement_v5/worker_1_ivani/rebuild`

See `verification.json` for reconstructed rows, scope checks and unchanged party-set outputs. The baseline builder retains its v4 version label in this isolated run; no builder/version change is part of this worker's scope.
