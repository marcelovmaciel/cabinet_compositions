# Independent bounded review: C069–C071

Reviewed 2026-09-10. Canonical files were read, not edited.

## C069: Mário Ramos Ribeiro — approved

The preserved TSE record has `dtFiliacao=[1997,1,31]`, PSDB, regular registration, no pending marker, and no departure/cancellation/exclusion. This is an explicitly historical joining date, not an undated current label. Its documented continuity supports the qualifying service `[2018-04-06,2018-04-10)`.

Independently recomputed the identifier hash from the preserved official 2011 FAPESPA document. It exactly matches the scoped TSE record (`3d6f9994…`), and the surrounding text identifies Mário as FAPESPA president. No identifier was copied into the review. No new substantive conflict found.

## C070: Wallace Nunes da Silva — approved; Rio homonym rejected

The Belford Roxo/UNIÃO record dates affiliation to 2022-03-20, with regular registration and no departure or pending marker. This supports continuity through `[2023-07-14,2023-07-18)`. Independently re-read the official Ministry of Tourism designation preserved in `followup_root/web_registry_02.json` and made one fresh scoped party/municipality query. Both the preserved full identifier hash and the official six-digit masked identifier segment match that record.

The Rio de Janeiro/PT record, dated 2011-03-29, has a different identifier hash. It is an exact-name homonym, not a historical party change by the minister:

| Source extract | Identity hash | Disposition |
|---|---|---|
| `followup_root/tse_RJ_6865_72.json` | `b772f82de18380527d23f5be9f44bc4581147db236afedc6b23f8f9448d2f70e` | Matched cabinet officeholder; UNIÃO |
| `followup_root/tse_RJ_7043_47.json` | `76c6ad45176a41fcc1fc6695bbd5212c13d0ad814fd6669553c6ea08f7720f86` | Different identified person; reject PT assertion |

The root identity-verification file was not overwritten.

## C071: Helder Melillo — identity and dated entry approved; interpretation caveat

Independently recomputed the hash from the preserved official 2020 MDR designation. It exactly matches the scoped TSE record (`62357a61…`). The historical NOVO entry on 2017-10-28 is supported.

The record simultaneously contains `dtDesfiliacao=[2021,2,3]`, `cdMotivoDesfiliacao=2`, `stRegistroFiliacao=1`, `indPendencia=1`, and `tsCadastroDesfiliacao=null`. The manual establishes that a regular registration may retain a pending departure. However, its pending category covers voluntary request, expulsion, and statutory departure. The reason-code mapping has not yet been independently decoded. The manual also distinguishes the party's departure-entry date from a Justice-registered departure date; the actual API field combination must remain inspectable instead of relabeling the date as an established request date.

The [official resolution](https://www.tse.jus.br/legislacao/compilada/res/2019/resolucao-no-23-596-de-20-de-agosto-de-2019) was independently read. Article 24 preserves the registration when voluntary departure has not been communicated to electoral authorities. Article 21 separately provides immediate cancellation grounds for expulsion and statutory departures. Therefore the record permits an explicit **formal-registry primary adjudication with a genuine unaffiliated alternative**, but does not establish that the 2021 event was necessarily a voluntary request awaiting processing or that continued NOVO affiliation is legally certain. Preserve both dates, reason code, pending marker, and the two-day set-changing alternative. Do not convert this finding to an exact affiliation observation. A six-endpoint public metadata check did not supply the reason-code definition (`helder_public_metadata_probe.json`).

## Metadata correction recommended

`evidence.csv` currently places historical affiliation event dates in the `publication_date` field for all three new records. Those event dates should remain in the raw registry and rationale. The source publication date is unknown; retrieval date is the 2026 observation. This does not change the supported service-date reconstruction.

## Legacy-manual follow-up

The independently read legacy manual distributed in 2019 (`../followup_bolsonaro_affiliations/tse_filia_manual2019.txt`, around line 825) explicitly treats a party-requested departure lacking electoral-authority communication as a pending-cancellation certificate, rather than a non-affiliation certificate. This supports the plausibility of a legacy party-departure date persisting in the current record and strengthens the formal-registry primary rationale. It still does not establish the migration mapping or decode Helder's reason code. The pending departure and unaffiliated alternative remain necessary.
