#!/usr/bin/env python3
"""Adaptasi Cloudflare report-schema.json untuk bug bounty Muse.

Perubahan vs upstream (MIT, github.com/cloudflare/security-audit-skill):
- Trace/evidence item: lokasi boleh SOURCE (file+line, repo-relative) ATAU
  LIVE (url + optional method/request/response) — satu lokasi per entry,
  enforced via oneOf. Upstream hanya mengenal file+line (audit source).
- Selain itu skema IDENTIK dengan upstream (3 verdict, severity, dsb).
- Validator .cjs tidak diubah sama sekali; ia membaca report-schema.json
  dari direktorinya sendiri, jadi skema adaptasi ini yang dipakai.

Jalankan: python3 adapt-schema.py
Input : ../security-audit-ref/skills/security-audit/report-schema.json
Output: ./report-schema.json
"""
import json
import pathlib

SRC = pathlib.Path(__file__).parent.parent / "security-audit-ref" / "skills" / "security-audit" / "report-schema.json"
DST = pathlib.Path(__file__).parent / "report-schema.json"

schema = json.loads(SRC.read_text())

TRACE_PROPS = {
    "kind": {"type": "string", "enum": ["entrypoint", "propagation", "sink"]},
    "file": {"type": "string", "minLength": 1},
    "line": {"type": "integer", "minimum": 1},
    "url": {"type": "string", "minLength": 1},
    "method": {"type": "string", "minLength": 1},
    "request": {"type": "string"},
    "response": {"type": "string"},
    "scope": {"type": "string", "minLength": 1, "visibleContent": True},
    "description": {"type": "string", "minLength": 1, "visibleContent": True},
}
EVIDENCE_PROPS = {
    "file": {"type": "string", "minLength": 1},
    "line": {"type": "integer", "minimum": 1},
    "url": {"type": "string", "minLength": 1},
    "method": {"type": "string", "minLength": 1},
    "request": {"type": "string"},
    "response": {"type": "string"},
    "description": {"type": "string", "minLength": 1, "visibleContent": True},
}
LOC_ONEOF = {"oneOf": [{"required": ["file", "line"]}, {"required": ["url"]}]}

patched = {"trace": 0, "evidence": 0}


def patch(node):
    if isinstance(node, dict):
        props = node.get("properties")
        if isinstance(props, dict) and "file" in props and "line" in props:
            if "kind" in props:  # trace item
                node["properties"] = TRACE_PROPS
                node["required"] = ["kind", "scope", "description"]
                node.update(LOC_ONEOF)
                patched["trace"] += 1
            elif "description" in props and "scope" not in props:  # evidence item
                node["properties"] = EVIDENCE_PROPS
                node["required"] = ["description"]
                node.update(LOC_ONEOF)
                patched["evidence"] += 1
        for v in node.values():
            patch(v)
    elif isinstance(node, list):
        for v in node:
            patch(v)


patch(schema)
assert patched == {"trace": 3, "evidence": 3}, patched

schema["$comment"] = (
    "ADAPTASI Muse (2026-11-14) dari Cloudflare security-audit-skill "
    "(MIT): trace/evidence boleh SOURCE (file+line) ATAU LIVE (url). "
    "Satu lokasi per entry (oneOf). Selain itu identik dengan upstream. "
    "Validator validate-findings.cjs TIDAK diubah."
)

DST.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
print(f"patched={patched} -> {DST}")
