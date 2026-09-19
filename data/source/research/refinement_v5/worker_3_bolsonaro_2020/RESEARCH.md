# Worker 3: Bolsonaro 2020 vacancy actors

Research date: 2026-09-10, Brasilia civil date (some HTTP logs are already 2026-09-11 UTC).

## Scope and retained baseline

Assigned people and half-open service intervals: Marcos Paulo Cardoso Coelho da Silva, Casa Civil, 2020-02-14/2020-02-18; Luiz Pontel de Souza, Justice, 2020-04-24/2020-04-29; Renato de Lima Franca, AGU, 2020-04-28/2020-04-29. Their actual vacancy service was already adjudicated. Nothing new contradicts it; all service records and the global service rule are unchanged.

The assignment's complete relevant affiliation, service, evidence, decision, blocker, research-register and residual-uncertainty rows, the codebook, and retained source contexts were reviewed. `prior_files.json` lists all 26 retained referenced files; `prior_review_inventory.json` records hashes and line counts. `prior_target_blocks.json` preserves the target-bearing source blocks extracted during review, including repeated extracts and unrelated material sharing an official page. The retained web files are search results/excerpts, not necessarily full original sources.

Prior established failures matter: all 35 historic 2016 Brasilia party lists; current all-party Brasilia and Sao Paulo lists; the historical nationwide name queries; and Renato's 2016 PT Araucaria same-name lead and all 39 current Araucaria party lists. Those registry scans were not repeated. The PT historical row lacks a bridge from its masked voter number to the AGU officeholder. It remains an unconfirmed possible homonym, not a credible personal PT alternative. The blocked historic ZIP and Brasil.IO-login routes were not bypassed or retried.

The prior contemporary news about Luiz Pontel and Guilherme Theophilo explicitly attributes PSDB departure to Theophilo. Prior Marcos sources establish police/association employment, appointment and actual vacancy replacement. Prior Renato sources establish legal-government employment and substitute service. None is a personal non-affiliation observation.

## New channels and findings

### Luiz Pontel: official registry in additional biographically justified places

The official MJ 2018 team profile's indexed text identifies Sananduva as his birthplace. Its current original URL redirects to a login page: `https://www.gov.br/mj/pt-br/assuntos/noticias/collective-nitf-content-1546435379.86/documentos/Perfildaequipe.pdf`. We retain the response as `mj_2018_profiles.login.html`, not as a PDF, with corrected retrieval metadata; no login was attempted. The prior Portal Prudentino and Folha de Londrina records establish his work in Presidente Prudente and Londrina. These locations justify a bounded search; employment does not establish electoral domicile or affiliation.

The official public TSE app was queried using its documented municipality and party-list routes. `scan_tse_new_localities.py` adapts the earlier read-only script, with the exact target name limited to LUIZ PONTEL DE SOUZA. Accent normalization and case normalization precede exact equality; other voters are processed transiently and discarded. Every request's URL, returned count, total count, timestamp and whole-response SHA256 are retained. Public numeric municipality IDs come from `/v1/localidade/{state-object-id}/municipios`.

| Municipality | Party identifiers | Pages | Rows inspected | Exact matches | Errors |
|---|---:|---:|---:|---:|---:|
| Londrina | 39 | 39 | 37,726 | 0 | 0 |
| Sananduva | 39 | 39 | 2,034 | 0 | 0 |
| Presidente Prudente | 39 | 39 | 14,473 | 0 | 0 |
| Total | 117 queries | 117 | 54,233 | 0 | 0 |

Consolidated retained source: `sources/tse_pontel_all_new_localities.json`; summary: `sources/TSE_NEW_LOCALITIES_SUMMARY.json`; individual query logs also retained. These are current locality lists, not a complete national historical universe for April 2020. Their absence cannot establish non-affiliation, a departure date, or a finite set of possible parties. V5W3E001/V5W3D001 preserve UNKNOWN.

### Renato: actual corporate eligibility document

The prior identity lead points to [Caixa Seguridade committee minute 104, March 14, 2022](https://api.mziq.com/mzfilemanager/v2/d/3972906b-e50b-4f74-ab74-4d0d32125d11/4b015055-675f-db8a-8597-81266eb9317a?origin=1). The original two-page PDF was retrieved and read. Its item 1 identifies Renato as an XS3 fiscal-council nominee, and item 1.1 records approval with a reference to Opinion 014/2022. The minute does not contain the opinion or any declaration about political-party affiliation. Approval alone is not a negative affiliation certificate.

`renato_caixa_eligibility_scoped.txt` retains the complete target item and its source details, with the public personal identifier redacted. Original-PDF response hash and retrieval information are in `renato_caixa_eligibility_20220314_retrieval.json`; unrelated nominees' identifiers were not retained. Full raw PDF, text and temporary rendering were removed after scope review. The two-page original was also opened through the web tool; `web_008.json` retains the extract with identifiers redacted. The local image-view helper failed because of the environment's bwrap startup issue; no claim about a new authored PDF's layout is involved.

Queries for the underlying Opinion 014/2022, XS3, forms and personnel declarations found the same minute, corporate accounts and general legal/career documents; no underlying personal affiliation declaration was recovered. The 2023 corporate assembly declaration concerns eligibility for commercial/public office and specified convictions, not party membership. It also postdates the assigned interval. V5W3E002/V5W3D002 retain UNKNOWN and explicitly reject using the minute to confirm the historic PT Araucaria lead.

### Marcos: primary professional-association source and declaration search

The [ADPF original 2021 elected regional-directory publication](https://web.adpf.org.br/noticia/adpf/eleicoes-2021-diretorias-regionais-da-adpf-sao-empossadas/) was retrieved directly after the web-tool fetch timed out. Its complete Distrito Federal entry lists Marcos Paulo Cardoso Coelho da Silva as treasurer. Scoped text and whole-response hash are in `adpf_2021_scoped.json`.

This source identifies the body involved in the earlier desfiliação reports as the professional police-delegates association. Association membership and its termination cannot be read as political-party membership or departure. Likewise later institutional testimony about Anderson Torres, police employment, and friendship with Onyx Lorenzoni do not identify Marcos's personal party status. Searches for an actual declaration, personnel form, or explicit non-affiliation statement recovered no qualifying February 2020 observation. V5W3E003/V5W3D003 retain UNKNOWN.

## Search record and limitations

`web_001.json` through `web_009.json` retain the new browser-result extracts/fetch results. Public personal identifiers in them were redacted before retention. Families used: exact names + declaration; Renato + eligibility/Caixa/Opinion 014/2022/XS3/forms; Pontel + official profile/certificate/DACP; Marcos full/short name + council/CV/declaration; exact personal non-affiliation wording. Several queries resurfaced already-reviewed wrong-person or wrong-subject results; these duplicates were screened, not counted as independent evidence. Long-name searches sometimes produced unrelated token matches. No inference is made from that search engine behavior.

The source channel is exhausted for the publicly retrieved materials, not for all possible records in existence. A future resolution needs a temporally relevant exact-person party/nonparty statement, a proper historical registry observation with identity, or an exact-person exhaustive negative covering the relevant universe/date. No such negative is claimed here. These findings support no finite sensitivity constraints; assigning arbitrary alternatives would invent evidence.

## Isolated implementation and verification

Inputs copied from `refinement_v5/baseline/inputs`. Three evidence and three decision rows added; five evidence/snapshot links added; three existing affiliation rows receive only new evidence/decision references; three existing research-register rows are extended. Affiliation states, parties, dates, support text, service rules and all services remain unchanged. All three assigned dependencies remain genuine completion blockers. No canonical inputs, releases, other worker inputs, manuscript or electoral data were edited.

`merge.json` contains exact upserts/deletes keyed by first CSV field (snapshot links use the composite). `snapshot_merge_map.json` gives local source paths, cabinet_dataset-relative destinations and SHA256. `verification.json` records builder success and unchanged party-set outputs. The isolated builder completed successfully with 4,096 daily rows and 100 unidentified days, matching the unchanged baseline scientific result. Parent is responsible for integration and code/tests.
