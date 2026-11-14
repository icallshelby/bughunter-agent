# Agentic Bug Hunter

A security agent that hunts vulnerabilities in smart contracts and protocols — and proves its findings instead of just claiming them.

**Entry for zkVerify Agent Games, Wildcard track** (competition 21 Oct – 21 Nov 2026).

## The problem

AI bug hunting is easy to fake. An agent can flood a programme with plausible-looking findings that waste triagers' time, or hallucinate a vulnerability that doesn't exist. For a hunter, an unproven finding is worthless; for a protocol team, it's noise. What both sides need is a finding that survives being attacked.

## Who it helps

- **Bug-bounty hunters** who want to file findings that hold up under triage instead of getting closed as invalid.
- **Protocol teams** who want signal, not volume: every finding this agent files carries machine-checkable evidence and a validator verdict.

## How it works

1. **Scope-first.** The agent never touches a target without an explicit programme and scope. No scope, no hunt.
2. **Recon.** `subfinder`, `httpx`, `nuclei`, `katana`, `amass`, `gau` and friends map the target's surface.
3. **Hunt.** An AI brain (Gemini via LiteLLM, Ollama `qwen3:4b` as fallback) reads the code and proposes candidate findings.
4. **7-Question Gate.** Every candidate must survive seven validation questions before it counts as a finding.
5. **Adversarial verifier.** A second, independent reviewer whose job is to *refute* each finding. Verdicts: `confirmed`, `needs_validation`, `rejected`.
6. **Deterministic validators.** Before anything is filed, `verifier/validate-findings.cjs` and `verifier/validate-coverage-ledger.cjs` check the report and the coverage ledger. A finding that fails validation never ships.
7. **Free-only.** No paid filing, no paid tooling, no paid model required.

## Key decisions

- **Verification is a separate seat from hunting.** The hunter never grades its own work. That separation is the whole point.
- **Evidence over claims.** A finding without a reproduction is not a finding.
- **Scope-first is a hard rule, not a preference.** It is what keeps the agent from becoming a scanner pointed at strangers.

## Evidence it works

`evidence/xe-9554-summary.json` — redacted summary of report **XE-9554**, filed 12 Nov 2026 against the XE Network bounty programme: 2 findings (1 High, 1 Medium claimed), both reproduced in the local harness (4/4 checks PASS) and both passing the deterministic validators. Status: awaiting triage. Full vulnerability mechanics and PoC code are withheld until triage — responsible disclosure.

The live demo endpoint serves this same summary at `GET /report`.

## Layout

- `skills/agentic-bug-hunter/` — the agent skill: the full hunt → gate → verify → report workflow.
- `verifier/` — deterministic validators for findings and coverage ledgers (adapted from Cloudflare's `security-audit-skill`, MIT), plus the report schema and a black-box sample.
- `evidence/` — redacted summary of a real filed report.
- `endpoint/` — the public demo endpoint (Node, zero dependencies).

## Setup

The hunting engine is a separate dependency, not vendored here:

```bash
git clone https://github.com/awarexone/agentic-bug-hunter  # upstream engine (MIT)
# install its recon toolchain per its own README, then point the skill at it
```

Run the demo endpoint:

```bash
node endpoint/server.cjs 8080
curl localhost:8080/        # agent card
curl localhost:8080/health  # liveness
curl localhost:8080/report  # redacted sample report
```

## zkVerify

No zkVerify integration is shipped yet, and none is claimed. What exists today: findings are already machine-checkable claims (schema + validator verdicts). The natural next step is making a validator verdict provable on-chain via zkVerify — so a triager can check "this finding was validated" without trusting the hunter. That is a direction, not a feature.

## Attribution

- Hunting engine: upstream `agentic-bug-hunter` (MIT).
- Verifier validators: adapted from Cloudflare's `security-audit-skill` (MIT), with the report schema extended for live (black-box) evidence.
