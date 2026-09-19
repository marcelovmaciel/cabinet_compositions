# Sérgio José Pereira: final bounded identity check

The twelve historical Filiaweb same-name leads do not establish the cabinet officeholder's affiliation. All twelve corresponding current TSE municipality/party queries succeeded and covered all 19,891 returned records. Renamed organizations were queried as PR → PL, PMDB → MDB, and PTdoB → Avante.

Five queries returned exact-name records: PP in Ibiúna, Miguelópolis, Umuarama and Itaúna, and PSB in Osasco. Each has a different personal identifier from the military officeholder identified in the Casa da Moeda assembly of 29 April 2021, published in the DOU on 25 May 2021. They are rejected homonyms, not party alternatives for the cabinet officeholder.

The seven other municipality/party lists returned no exact-name record. Current-list absence cannot identify the historical person, establish historical cancellation, or establish non-affiliation. These seven archival names remain unlinked leads; they are not evidence-supported personal party alternatives.

Consequently this check supplies no defensible affiliation adjudication and does not resolve Sérgio's remaining party-set dependency. No canonical data was changed.

The source URL, dated document metadata, original-response hash and scoped official identity hash are in `sergio_official_identity_reference.json`. Query URLs, full coverage counts, scoped matching rows, identifier hashes and individual dispositions are retained in `sergio_twelve_current_checks.json`. Full personal identifiers, addresses and unrelated public roster records were processed only in memory and are not retained in this extract.

The bounded research can be repeated from the repository root with:

```sh
python cabinet_dataset/research/followup_bolsonaro_affiliations/scan_sergio_historical_leads.py
python cabinet_dataset/research/followup_bolsonaro_affiliations/verify_sergio_identity.py
```

Live lists may change after retrieval. These scripts document the method; the retained scoped assertions document this retrieval.
