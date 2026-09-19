# Worker 4: March 2021 vacancy actors

Scope: personal affiliation on 2021-03-30 for Jonathas Assunção Salvador Nery de Castro, Otávio Brandelli and Sérgio José Pereira, plus Sérgio on 2021-03-31. The already adjudicated vacancy services and successor timing are retained. The root's later user-authorized primary-assumption layer is separate from this evidence-grounded patch.

## Existing trails read first

The assignment includes relevant v4 completion blockers, complete research-register records, affiliations, services, decisions C036/C058/C059/C063/C072, source assertions, residual-person uncertainty and MRE date sensitivity. The complete codebook and worker protocol were read. All 41 retained files named by the three research-register entries were processed and their exact-person source blocks inspected; `prior_review_inventory.json` records paths and original-byte hashes. Search logs frequently contain unrelated documents or unrelated party labels, which are not assertions about the officeholder. The complete historical Brasília scan findings, Sérgio's 12 historical-homonym checks and official identity reference were read. W5's final handoff and W6's public-registry scan code were also read. The prior current DF scan summary and scanner confirm 39 party queries and 231,889 rows, so that scan was not repeated.

Prior limits remain: career, employer, ministerial sponsor, routine substitute signatures and Bolsonaro's own party labels do not identify these people's memberships. A syndicated column repeats a rumor that Brandelli is a card-carrying PT member solely because of an INPI nomination by Mercadante; this is not a verified personal membership observation. Sérgio's historical exact-name hits were already rejected through identity mismatch or remained absent from current records. Current and 2016 municipal no-matches cannot establish nonaffiliation. W5's issuer-original Petrobras 2022 filing for Jonathas concerns corporate independence and politically exposed person status, not party membership.

## New Sérgio channel: original personnel eligibility assessment

The official CMB website links all 2021 eligibility minutes. The 57th meeting minute, 16 April 2021, specifically assesses Sérgio José Pereira for a vacant Fiscal Council seat. It records receipt of Ofício SEI 91287/2021/ME on 12 April, recognizes the required three years of management/advisory experience and compatible education, then finds requirements met and no impediments under the expressly cited fiscal-council provisions. It identifies prior SEI technical note 13261/2021/ME. The full one-page PDF was extracted and visually inspected; it contains no express party/nonparty declaration. It also postdates the two service dates. The neighboring 54th–56th minutes concern other people. The later 69th minute found through search concerns Thiago Meirelles's replacement of Sérgio: its self-declaration belongs to Thiago, not Sérgio.

Source: https://www.casadamoeda.gov.br/arquivos/lai/atas-do-comite-de-elegibilidade/57a-ata-de-reuniao-comite-de-elegibilidade-16-04-2021.pdf . Retained original `sources/cmb_57.pdf`, text, and official archive/index links. Evidence/decision: V5W4E001 / V5W4D001. Actual disposition: UNKNOWN retained, now explicitly documenting this newly examined channel.

## New Brandelli channel: original nomination dossier and identity-scoped registry extension

The Senate MSF 14/2021 original dossier `dm=8953346` contains the presidential message dated 15 April 2021, MRE exposure dated 14 April and the career CV. The CV is visually verified at original PDF page 4. It establishes the exact diplomat's identity and Garibaldi/RS birthplace. It does not declare party affiliation/nonaffiliation. The separately retrieved committee report `dm=8986660` similarly concerns professional biography and the OEA. The avulso `dm=8978718` is retained as a duplicate presentation of the dossier and not counted as independent corroboration.

URLs: https://legis.senado.leg.br/sdleg-getter/documento?dm=8953346 ; https://legis.senado.leg.br/sdleg-getter/documento?dm=8986660 .

Using the same documented official public TSE client endpoint as W6, a new scoped lookup covered all 39 party IDs for Garibaldi (municipal object 7733). All requests succeeded: 3,030 current returned rows, no exact Otávio Brandelli. The script retains only target matches, counts, request URLs, timestamps and full-response hashes, not unrelated persons. This locality was not previously scanned. Birthplace supplies a locality lead, not proof of electoral domicile. The current municipal regular-record relation is neither nationwide nor an exhaustive historical membership registry; therefore this no-match does not narrow admissible historical party alternatives. No new personal certificate was obtained.

Evidence/decision: V5W4E002 / V5W4D002. Actual disposition: UNKNOWN retained. The MRE linked succession constraint explicitly keeps its outgoing UNKNOWN state; incoming Carlos França remains UNAFFILIATED and the candidate dates remain March 30 and 31.

## New Jonathas channel: pre-service Terracap personnel declaration

A public third-party mirror reproduces a Terracap eligibility minute dated 16 October 2019, naming Jonathas for a shareholder-Union Council seat and identifying process 00111-00010585/2019-82 and Ofício SEI 25400/2019/ME. It says the candidate provided a standard eligibility declaration and unspecified negative certificates from several institutions including TSE, plus a CV and voter document. It does not reproduce a party-affiliation certificate or its type, date, text or national/date coverage. The body says 19th meeting while the footer says 17th, another reason not to overstate verification. The official Terracap archive returned HTTP 403, also confirmed through the web retrieval tool. The mirror is labeled as such; no original-source retrieval is claimed. No access control was bypassed and no request was sent to another person.

URLs: https://pt.scribd.com/document/1057191170/Ata-Terracap ; https://www.terracap.df.gov.br/index.php/orgao-colegiado/contexto-atas-age .

An unspecified TSE negative certificate could address several matters and cannot be recoded as a party-membership negative. Compliance with corporate eligibility likewise does not assert the absence of ordinary membership. Evidence/decision: V5W4E003 / V5W4D003. March 2021 UNKNOWN retained. No December 2022 affiliation row was edited; W5 owns that interval. The shared research-register upsert appends this finding to the baseline; root must combine it with W5's separate appended finding rather than overwrite either.

## Implemented patch and constraints

Three relevant affiliation rows keep their states, dates, parties and alternatives unchanged and gain precise support/evidence/decision fields. Three new evidence rows and three decisions explicitly distinguish tested source semantics. Three research-register entries gain these new channels and retain `blocked` historical status. One MRE service-sensitivity constraint gains the explanatory finding and source link but no changed outgoing/incoming state or dates. No services, party identities, global service rules or builder code change. Snapshot links use final paths relative to `cabinet_dataset`: `research/refinement_v5/worker_4_bolsonaro_2021/...`.

`merge.json` contains upserts/deletes relative to the immutable baseline. `inputs/decisions.csv` in the inherited historical snapshot link remains the original baseline pointer/hash; no hash was silently rewritten to modified decisions. Root already handles that canonical historical-source pointer. `sources/` and this research file are to be copied to the matching final research directory. `review/` images are scratch QA and need not enter the release.
