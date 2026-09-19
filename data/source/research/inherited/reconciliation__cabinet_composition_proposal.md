# Proposed cabinet-composition reconstruction, 2015–2026

**Status:** analytical proposal for review, not an approved dataset or an exhaustive daily chronology.

**Coverage:** 1 January 2015 through 19 March 2026, inclusive. No electoral quantities have been recalculated.

## What was compared

The uploaded contemporaneous-affiliation audit (`audit.zip`), the uploaded Atlas CSV
(`7010-261partidogabineteministerio.csv`), and selected additional documentary checks.

The Atlas contains 708 records. Of these, 221 concern the paper's administrations:
67 Dilma II, 59 Temer, 58 Bolsonaro, and 37 Lula III. Rows are not necessarily distinct
appointments: one ministerial tenure can occupy several rows when a recorded attribute changes.
The 221 relevant records are included in `atlas_relevant_rows.csv`, preserving original CSV
row numbers. The duplicate original date-column names have been disambiguated rather than
overwritten.

`atlas_audit_reconciliation.csv` records 30 material case-level comparisons. It is not an
exhaustive certification of every person, date, or office. The original audit remains the
source for the evidence IDs used below.

## 1. Assessment of the audit

The audit establishes defects in office coverage, party parsing, dates, and time-varying
affiliation. It does not provide a completed replacement chronology. Its 257 inherited
appointment records are not a complete census; the pinned tables contain 273 person rows,
but the extra rows are heterogeneous and cannot simply all be included. The prior
138 PARTY, 76 UNAFFILIATED, and 43 UNRESOLVED classifications refer to appointment-date
claims, not validated entire tenures.

The concrete PR/Paraná parser defect is particularly important: it explains a missing
political party independently of any theoretical disagreement about cabinet coalitions.
Missing Temer MDIC and MMA records similarly require additions independently of the
choice between appointment-time and contemporaneous affiliation.

The audit's `legacy_set_comparison.csv` deliberately leaves all proposed complete
contemporaneous sets null. Its 32 rows are comparison intervals, not a new count of
cabinet periods.

The design is broadly suitable: reviewed offline histories produce a versioned cabinet
dataset, while election-year mappings and electionsBR remain in a separate consumer.
But the next substantive task is resolution of first/last party witnesses and disputed
dates, not another broad architecture exercise.

The completeness flags should not be interpreted as saying that every unknown biography
changes a cabinet set. A change from PSD to MDB may be composition-neutral when both
parties have other definite officeholders. Conversely, a sole party witness can matter
even during a short legally effective absence.

### Additional issue found in this review

Fernando Coelho Filho's official Chamber biography records a notice dated 22 February 2018
communicating PSB-to-no-party change, followed by DEM membership. Atlas retains PSB through
April 2018. The notice date is not automatically the effective affiliation date.

The biography also records several returns to his parliamentary mandate during ministerial
service, including 18–25 October 2017. These are leads requiring comparison with effective
dismissal/reappointment and replacement records. They cannot be smoothed automatically as
ordinary temporary delegation. If he was the last PSB witness and was no longer minister,
the party set changes.

Source: https://www.camara.leg.br/deputados/141431/biografia

## 2. How Atlas should be used

Use `Partido do Ministro` as the relevant affiliation assertion.
Preserve `Partido da Pasta` as a different variable, not as a replacement when they disagree.

Atlas is another compilation to reconcile, not a validated gold standard. Its source
genealogy has not been established here, so agreement must not automatically be described
as statistically or documentarily independent corroboration.

It correctly records Fábio Faria's PSD-to-PP change on 24 March 2022, but misses other
time-varying changes. Examples include Hilton's PROS membership, Salles's NOVO sanctions,
Marinho's PSDB departure, Pontes's later party identities, and Tarcísio's Republicanos
membership at the end of his ministry.

Atlas gives Henrique Meirelles as PSDB during Temer; the audit supports PSD at entry and
MDB from 3 April 2018. It gives Ronaldo Fonseca as Podemos at ministerial entry, whereas
the prior audit cites a party disaffiliation notice four days earlier. The notice's direct
URL is currently unavailable, so recovering or corroborating it remains necessary.

Atlas gives Valter Casimiro PR throughout his ministry; the audit distinguishes PR
nomination from membership and records a conflicting later no-party roster. Do not
resolve that conflict merely by choosing the institutionally more prestigious database.

Atlas's last recorded Lula III entry is 13 September 2023; 34 of 37 Lula III rows have
blank exits. This is not coverage of subsequent history through March 2026. Nor does
the omission of GSI demonstrate that its occupant was unaffiliated.

## 3. Recommended primary definition

At each date, record the formal party affiliations of people holding qualifying cabinet
offices in the administration being studied.

Include ordinary ministries and other offices with dated legal Minister of State status.
Count titular incumbents who retain legal title during ordinary delegation. Count acting
incumbents filling genuine vacancies. A legally effective resignation and reappointment
must be recorded as such, even when motivated by a temporary parliamentary return.

Use effective service and dated personal affiliation, not nomination, public ceremony,
party sponsorship, party-leadership support, or parliamentary alignment. A political
suspension and formal cancellation of membership require separate treatment.

Separate the incoming administration's transition offices from the outgoing administration's
cabinet. A legally ministerial transition appointment can belong in the reusable officeholding
dataset without being assigned to the outgoing president's cabinet party set.

Use stable organization identities, dated merger/incorporation events, and a documented
daily closing-state convention. Pure renames do not constitute political entry or exit.

Do not automatically add a federation's other constituent parties. Do not add the
president's or vice-president's party unless independently represented by a qualifying
officeholder.

### Status of the sets below

These are recommended candidate compositions and documented transitions, not a claim that
all omitted offices and histories have been ruled out. They are not suitable as a
machine-readable production release without the specified adjudications.

Stable-looking ranges can contain short actual-service interruptions. Where a date is
unresolved, the proposal does not assign a convenient precise day. An unknown additional
affiliation must not be silently converted to no party.

## 4. Dilma II

Recommended initial set:

**PCdoB, PDT, PMDB, PP, PR, PRB, PROS, PSD, PT, PTB.**

PROS is supplied by Cid Gomes; it is not an electoral-mapping addition.

| Stage | Proposed party set | Required adjudication |
|---|---|---|
| Initial cabinet, 1 January 2015 | PCdoB, PDT, PMDB, PP, PR, PRB, PROS, PSD, PT, PTB | Complete scope and service checks; Cid's eventual effective departure |
| After Cid's departure in March 2015 | PCdoB, PDT, PMDB, PP, PR, PRB, PSD, PT, PTB | Do not interpret the Atlas last-date field mechanically |
| From Hilton's documented 18 March 2016 party switch while still minister | PCdoB, PDT, PMDB, PP, PR, PROS, PSD, PT, PTB | Last PRB/other PROS witnesses and effective office end |
| After Hilton leaves | PCdoB, PDT, PMDB, PP, PR, PSD, PT, PTB | Atlas and old source-derived departure dates disagree |
| After Occhi leaves | PCdoB, PDT, PMDB, PR, PSD, PT, PTB | Effective PP exit, not announcement alone |
| After Kassab leaves, before Temer assumes government | PCdoB, PDT, PMDB, PR, PT, PTB | Effective PSD exit; Atlas gives 19 April rather than the old earlier boundary |

This changes the historical sequence before electoral arithmetic. The old two-day April
inversion duration is not justified merely by accepting the Atlas party labels: its
boundary dates need direct resolution.

Hilton switch:
https://exame.com/brasil/hilton-troca-o-prb-pelo-pros-para-nao-perder-ministerio/

## 5. Temer

Recommended initial set, from the beginning of his exercise of government in May 2016:

**DEM, PMDB, PP, PPS, PR, PRB, PSB, PSD, PSDB, PTB, PV.**

PR is supplied by Quintella, PRB by the MDIC ministers, and PV continues through
Edson Duarte after Sarney Filho. PTB is supplied by Nogueira and Yomura, subject to the
succession dates and any genuine vacancy.

The major trajectory should be reconstructed as follows:

| Stage | Proposed membership treatment |
|---|---|
| Initial cabinet | Eleven-party set above, with genuine service interruptions preserved |
| PSB withdrawal from political support in 2017 | Not sufficient to remove PSB if Coelho Filho remains formally affiliated and in office |
| Coelho Filho's formal departure from PSB | Remove PSB if he is the last witness; recover the effective date instead of using the later Chamber notice as an event date |
| Jungmann's 21 March 2018 departure from PPS | Remove PPS if no other PPS officeholder remains |
| Quintella's 2 April 2018 exit | PR continuation depends on Valter Casimiro's actual affiliation, not sponsorship |
| Mendonça Filho's April 2018 exit | Remove DEM if no other DEM witness remains |
| Fonseca's May 2018 entry | Do not automatically add Podemos; resolve the cited prior disaffiliation |
| Yomura's July 2018 exit | Remove PTB if no other PTB witness remains |

For late 2018, the supported starting point for adjudication is:

**MDB, PP, PRB, PSD, PSDB, PV**, with **PR unresolved through Valter Casimiro**
and **Podemos disputed through Ronaldo Fonseca**.

That is a confirmed-core proposal, not a complete set with unknowns deleted.
The recommended treatment of Fonseca is no-party if the cited 24 May termination
is recovered or corroborated. It is not acceptable to retain Podemos solely because
Atlas and the old Wikipedia-derived assignment agree.

Source of the cited Fonseca notice, presently unavailable by direct fetch:
https://www.podemos.org.br/podemos-desfilia-deputado-federal-ronaldo-fonseca-df/

Coelho Filho's official biography:
https://www.camara.leg.br/deputados/141431/biografia

## 6. Bolsonaro

Recommended initial set:

**DEM, MDB, NOVO, PP, PSL.**

The initial PP witness is Damares, not Ciro Nogueira. Do not back-project later party
memberships of Tarcísio or Torres, or automatically add PATRIOTA through Heleno.

### Events governing the 2019–2021 sequence

- NOVO: Salles's October 2019 suspension, May 2020 expulsion, and any appeal/effective
  cancellation require adjudication. Do not retain NOVO throughout 2021 simply because
  he remained minister.
- PSDB: Marinho's ministerial entry adds it in February 2020. The June 19, 2020 report
  says he had left a few days earlier. His continuing service does not preserve PSDB.
- MDB: resolve Osmar Terra's February 2020 effective departure.
- PSD: Fábio Faria supplies it from 17 June 2020.
- PSC: Gilson Machado supplies it from his effective Tourism entry in December 2020.
- Republicanos: João Roma supplies it from his effective entry in February 2021.
- PL: official records support Flávia Arruda's service from **31 March 2021**, not the
  disputed 20 March date or the Atlas's 6 April ceremony date.
- PP: Damares's departure is uncertain. Ciro creates an independent PP witness from
  his effective Casa Civil entry, whose appointment/assumption dates must be reconciled.

Accordingly, for the portion after Flávia's March 2021 entry and before Ciro's entry,
the proposed documented-party configuration is:

**DEM, PL, PSC, PSD, PSL, Republicanos**, with **PP dependent on Damares's
then-current membership**. Excluding NOVO rests on resolving the formal effect of
Salles's sanctions; PSDB is not supplied by Marinho during 2021.

After Ciro has actually taken office, the proposed main configuration is:

**DEM, PL, PP, PSC, PSD, PSL, Republicanos.**

This is not the previous nine-party frozen-affiliation configuration. No inversion
count is inferred here.

Sources:
https://www.camara.leg.br/deputados/204354/biografia
https://www.cnnbrasil.com.br/politica/ministro-de-bolsonaro-marinho-deixa-o-psdb/
https://exame.com/brasil/ricardo-salles-diz-que-foi-expulso-do-partido-novo/

### Early and late 2022

Following the 8 February merger, the corresponding proposed set is:

**PL, PP, PSC, PSD, Republicanos, União.**

March 2022 must be reconstructed as a short event sequence, not one bulk reform:

| Event | Composition question |
|---|---|
| Fábio Faria joins PP, 24 March | Does PSD disappear until Marcos Montes enters on 31 March? |
| Pontes and João Roma join PL, 27 March | Is this the last União witness? Is Republicanos briefly unrepresented? |
| Damares and Tarcísio join Republicanos, 28 March | Republicanos has new witnesses, independently of Roma |
| Gilson Machado joins PL, 30 March | Does PSC cease to be represented before his office exit? |
| Ministerial departures and new incumbents around 31 March | Verify whether PL loses its final witness and PSD returns through Montes; Republicanos continues through Cristiane Britto |
| Sachsida enters in May | His party history is unresolved; Atlas's no-party label conflicts with prior DEM evidence and unverified organizational continuity |

The proposed late-2022 **documented core** is:

**PP, PSD, Republicanos.**

It must not be published as the exhaustive set until Sachsida's possible União membership,
Heleno's disputed later history, and any other missing-scope/affiliation additions are
resolved. Atlas alone does not establish their absence.

Faria's dated party announcement:
https://progressistas.org.br/noticias-progressistas/fabio-faria-e-neucimar-fraga-chegam-para-fortalecer-o-progressistas/

## 7. Lula III

The comparatively stable proposed sequence is:

| Range | Proposed party set |
|---|---|
| 1 January–12 September 2023 | MDB, PCdoB, PDT, PSB, PSD, PSOL, PT, REDE, União |
| From 13 September 2023 until loss of the final União-affiliated minister | MDB, PCdoB, PDT, PP, PSB, PSD, PSOL, PT, REDE, Republicanos, União |
| After that loss through 19 March 2026 | MDB, PCdoB, PDT, PP, PSB, PSD, PSOL, PT, REDE, Republicanos |

The proposed date for the final União change is **8 December 2025**, the membership
cancellation documented by the audit for Sabino, not the old late-December ministerial
departure boundary. This requires confirmation that Sabino was the final personally
affiliated witness and that no successor acquired affiliation.

Waldez's PDT affiliation is not replaced by the party that sponsored his portfolio.
Frederico Siqueira and Gustavo Feliciano must not be made União members solely from
nomination. Fufuca's removal from PP internal leadership does not itself remove PP.
Anielle joining PT does not alter the set when PT is already represented.

Atlas supports the initial memberships and the September 2023 additions. It does not
establish a complete chronology through 2026. In particular, its omission of GSI does
not resolve Amaro's affiliation from May 2023. Unknown extra parties and genuine
short service interruptions remain separate checks; the table is not a claim of
three certified maximal periods.

Sabino cancellation source cited in AFF-036:
https://agenciabrasil.ebc.com.br/politica/noticia/2025-12/uniao-brasil-decide-expulsar-ministro-celso-sabino-da-legenda

## 8. Paper integration and remaining decision boundary

The cabinet dataset must preserve contemporaneous parties and actual service.
The consuming paper separately maps these parties into election-year accounting
units and retains its chosen election-year votes and seat vector. Contemporary
ministerial changes do not, by themselves, authorize tracking parliamentary defections
or changing election totals.

A whole-party merger can be represented organizationally without allocating votes.
A split or otherwise ambiguous electoral ancestry requires a consumer-level rule.
Do not repair that ambiguity by changing the historical cabinet membership.

For the paper, the recommended primary input is a release with supported compositions,
explicitly unresolved intervals, and witness/provenance records. Do not fabricate a
complete daily series to meet a production schema. Where the alternatives are finite
and exhaustive, later electoral analysis can report classification across all of them.
Where an additional party remains unspecified, the interval is not fully identified.

No new cabinet-period total, inversion count, inversion-day total, or decomposition is
established by this proposal. The old Temer and Bolsonaro sets cannot simply be preserved.
The conditional appointment-time Bolsonaro episode is also not a verified fallback.
The ideological results were not recomputed or assessed by this review.

The principal remaining work is targeted adjudication of actual first/last witnesses and
effective dates: Dilma's March–April 2016 boundaries; Temer service interruptions,
Coelho Filho, Casimiro and Fonseca; Salles/Damares/Marinho and March 2022; late-2022
Sachsida/Heleno; and Lula's missing-office affiliations and final União witness.

The next implementation prompt should follow approval of this definition and proposed
membership trajectory, not precede it.
