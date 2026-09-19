"""Compare the five same-name registry hits to the official officeholder identity.

Full identifiers and unrelated officials are processed in memory only.
"""
import datetime
import hashlib
import io
import json
from pathlib import Path
import re

import requests
from pypdf import PdfReader

HERE = Path(__file__).parent
URL = "https://www.casadamoeda.gov.br/arquivos/lai/atas-de-assembleias-gerais/AG-Ordinaria_29-04-2021-DOU-25-05-2021p122.pdf"
response = requests.get(URL, timeout=35)
response.raise_for_status()
document = "\n".join(page.extract_text() for page in PdfReader(io.BytesIO(response.content)).pages)
start = document.index("SÉRGIO JOSÉ PEREIRA")
identifier = re.search(r"CPF\s*([\d.]+-\d+)", document[start:start + 700]).group(1)
identity_hash = hashlib.sha256(re.sub(r"\D", "", identifier).encode()).hexdigest()
reference = {
    "name": "Sérgio José Pereira",
    "source_url": URL,
    "document_date": "2021-04-29",
    "publication_date": "2021-05-25",
    "response_sha256": hashlib.sha256(response.content).hexdigest(),
    "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "official_identity_sha256": identity_hash,
    "source_assertion": "Assembly elects Sérgio José Pereira, identified as military officer with Ministry of Defense identity, as CMB Fiscal Council member. Full personal identifier used only in memory for identity comparison; retained as hash. Address and unrelated officials discarded.",
}
(HERE / "sergio_official_identity_reference.json").write_text(json.dumps(reference, ensure_ascii=False, indent=2))
rows = json.loads((HERE / "sergio_twelve_current_checks.json").read_text())
for row in rows:
    assert row["status"] == 200 and row["records_inspected"] == row["totalElements"]
    for match in row["matches"]:
        same = match["public_registry_identity_sha256"] == identity_hash
        match["matches_official_general_identity"] = same
        match["disposition"] = "same_identity" if same else "rejected_homonym_identifier_mismatch"
(HERE / "sergio_twelve_current_checks.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
print({"queries": len(rows), "records_inspected": sum(row["records_inspected"] for row in rows),
       "identity_matches": sum(m["matches_official_general_identity"] for row in rows for m in row["matches"])})
