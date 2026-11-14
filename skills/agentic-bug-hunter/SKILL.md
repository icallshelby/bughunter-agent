# Agentic Bug Hunter

## Understand the request

- Bug bounty hunting with the Agentic Bug Hunter tool (AwareXone, MIT, repo
  https://github.com/awarexone/Agentic-Bug-Hunter): recon → hunt → validate →
  report, for HackerOne / Bugcrowd / Intigriti / Immunefi programs.
- Reply in Indonesian, short and direct. The submission report itself is in
  English, following the platform template.
- The user is HP-only. All hunting runs on this VM, never on the user's phone.

## Install state (verified 2026-11-12)

- Repo: `~/workspace/bughunter/repo` (v6.0.1, cloned 2026-11-12 10:46 WIB).
- CLI: `~/workspace/bughunter/venv/bin/bughunter` (Python 3.12 venv, package
  `agentic-bug-hunter` 6.0.1). Call it by full path; there is no global
  `bughunter` on PATH.
- Brain: Ollama local, free/offline, at `http://localhost:11434`.
  Model: `qwen3:4b`. Do NOT pull `qwen2.5:14b` / 32b models — this VM has
  7.7 GB RAM total and a 14b model does not fit.
- Config: `~/.bughunter/config.json` (created by `bughunter setup`).
  Output lands in `~/.bughunter/` and per-target `./findings`, `./recon`,
  `./reports` under the working directory.
- Recon tools (installed 2026-11-12, all free, verified 10/10):
  Go 1.27.4, nmap 7.94, subfinder v2.17.0, httpx v1.12.0, nuclei v3.11.1 +
  templates v10.5.2 (14.225 file di `~/nuclei-templates`), katana, ffuf
  2.1.0-dev, amass v4.2.0, gau v2.2.4, dalfox v2.13.0, subjack. Binaries in
  `~/go/bin` (+ `/usr/bin/nmap`); PATH persisted in `~/.bashrc`.
  Installer Linux: `~/workspace/bughunter/install-tools-linux.sh` — the
  repo's `install_tools.sh` is macOS/Homebrew and does not run on this
  Ubuntu VM. Notes: `~/workspace/bughunter/TOOLS.md`. Durable VM lesson:
  `/tmp` is only a 512 MB tmpfs — big Go builds must use
  `TMPDIR=$HOME/...` + `GOCACHE=$HOME/.cache/go-build`, never `/tmp`.
- NucleiFuzzer `nf` (ditambah 2026-11-14, repo 0xKayala): rantai
  ParamSpider + waybackurls + gauplus + hakrawler + katana → uro →
  httpx → nuclei fuzzing-templates; `--validate` konfirmasi SQLi via
  sqlmap / XSS via dalfox. `nf --doctor` semua OK kecuali subpipe
  (butuh API key, tidak diinstal). `--ai` MATI (butuh GEMINI_API_KEY,
  ngirim temuan ke Gemini — jangan aktifkan tanpa perintah).
  install.sh upstream TIDAK dipakai mentah (asumsi cwd = repo; pernah
  mengisi disk root sampai 100% — lihat TOOLS.md). Scope-first tetap
  berlaku: hanya untuk target dengan program/scope eksplisit.
- Foundry + Cargo (installed 2026-11-12, free): forge/cast/anvil 1.9.0,
  cargo 1.99.1 + rustc — for Solidity PoCs. Same `/tmp` rule applied
  (TMPDIR=$HOME/tmp-foundry).
- Install notes: `~/workspace/bughunter/INSTALL.md`.
- Upstream methodology lives in the repo, do not copy it here — read it
  when the task needs it:
  - Master workflow: `~/workspace/bughunter/repo/SKILL.md`
  - Plugin guide: `~/workspace/bughunter/repo/AGENTS.md`
  - Recon: `skills/web2-recon/SKILL.md`
  - Vuln classes + bypass tables: `skills/web2-vuln-classes/SKILL.md`
  - Methodology / mindset: `skills/bb-methodology/SKILL.md`
  - Validation: `skills/triage-validation/SKILL.md`
  - Reporting: `skills/report-writing/SKILL.md`
  - Payloads: `skills/security-arsenal/SKILL.md`
  - Web3 / token audit: `skills/web3-audit/SKILL.md`,
    `skills/meme-coin-audit/SKILL.md`
  - Rules always active: `rules/hunting.md`, `rules/reporting.md`

## Scope — program pilihan pengguna (12 Nov 2026)

Urutan: **XE Network dulu → HyperLiquid ke-2 → Ethereum Foundation
jangka panjang**. Detail scope terverifikasi di
`~/workspace/bughunter/SCOPE.md` §9–12. Hasil audit per program di
`~/workspace/bughunter/targets/<program>/`.

- **XE Network** (standing programme, testnet only): seluruh sistem
  in-scope, bayar maks 50.000 XE/finding (bukan USD, tanpa nilai dijamin).
  Status 12 Nov: audit emisi + quorum selesai, laporan C-H1 Medium +
  C-H2 High sudah difile-kan (targets/xe/REPORT-C-H.md, nomor konfirmasi
  menunggu hasil browser).
- **HyperLiquid** (bugbounty@hyperfoundation.org, KYC): bug node/API
  mainnet, testing HANYA testnet/local fork. Status 12 Nov: Bridge2 audit
  14 kandidat → 1 survivor Low (C2, replay updateValidatorSet, PoC Anvil
  2/2 PASS); SDK diff 8 kandidat → 0 survivor; HyperEVM sync 14 kandidat
  → 0 survivor. Faucet testnet BLOCKED: butuh deposit mainnet dengan
  alamat yang sama (≥5 USDC, BERBAYAR, tidak disetujui, tidak dilakukan).
  Black-box testnet butuh keputusan pengguna: deposit mainnet YA/TIDAK +
  mekanisme signing.
- **Ethereum Foundation**: spec + client EL/CL + compiler Solidity/Vyper +
  Deposit Contract, PoC wajib, testing local testnet, Critical maks $1 jt.
  Jangka panjang.
- **Revert Finance v4lend (Cantina) — TUTUP 3 Nov 2026, fase judging.
  JANGAN dihunt.** Kodenya hanya bahan belajar.
- **Metric (Immunefi)** — program baru dari pengguna 12 Nov 12:34 WIB,
  verifikasi scope masih jalan, belum hunting.
- Shortlist starter sebelumnya (Intigriti PWN, Kinepolis, Atlassian,
  GitLab, Shopify, GitHub, Immunefi, Beanstalk) tetap di SCOPE.md §1–8
  sebagai cadangan.

Wallet garapan bug bounty = wallet luar pengguna `0x8329…8b8a` (alamat
identitas/payout saja — asisten TIDAK pegang kuncinya, kunci penuh di HP
pengguna, jadi TIDAK BISA sign/transaksi dari wallet itu; sign testnet
tetap urusan pengguna dari HP). BUKAN calle (0x402F…9963).

## Scope first — hard rule

- NEVER hunt a target the user did not name with an explicit program/scope.
  Before any recon, confirm: program name, platform, and the exact in-scope
  asset list. Verify the asset is in scope (read the program page first).
- Out of scope, staging/dev unless explicitly listed, third-party services
  the target merely uses (Stripe, Salesforce, Google Auth), and anything
  without a bounty program are all NO — do not touch them.
- Credential attacks (wordlist-gen, osint-employees, breach-check, spray)
  are opt-in only: they need a separate explicit go from the user for that
  exact target, and spray itself always stops for a human go/no-go.
- No destructive testing: no data deletion, no mass account actions, no
  denial-of-service, no payload that corrupts state. Stop on a block, 429,
  WAF challenge or rate limit — do not route around it.

## Free-only

- Brain is Ollama local only by default. No paid provider (Claude / OpenAI /
  Grok / OpenRouter / Requesty) and no paid API key without a separate explicit
  order from the user for that exact provider.
- User reaffirmed 2026-11-12: "KLO bayar jangan" — if it costs money, do
  not do it. Any step that turns out to need payment stops there; report
  it first, never proceed silently.
- Gemini as bughunter brain does NOT work through the built-in provider
  (verified 2026-11-12): brain.py sends the key as `Bearer`, but the
  connector key only swaps in via the `x-goog-api-key` header — direct
  test returned HTTP 400 "Please pass a valid API key". The native
  endpoint with `x-goog-api-key` does reach Google, but the free quota
  for gemini-3.8-flash (20 req/day) was exhausted on 12 Nov (HTTP 429,
  reset ±15:15 WIB).
- JALUR PRO (TERVERIFIKASI JALAN 14 Nov 04:23 WIB): LiteLLM 1.109.1 di venv;
  launcher `~/workspace/bughunter/bughunter-litellm.sh` menyuntik surrogate ke
  GEMINI_API_KEY + BRAIN_PROVIDER=litellm. Model default
  gemini/gemini-3.1-flash-lite — tes chat langsung balas "OK". Model utama
  gemini-3.8-flash sedang 503 overload saat dites 14 Nov 04:21–04:23 WIB
  ("high demand, try again later", BUKAN kuota habis) — pakai via
  `BRAIN_MODEL=gemini/gemini-3.8-flash` kalau 503 sudah reda. Perbaikan
  proxy (14 Nov): no_proxy bawaan VM berisi entri IPv6 berkurung
  "[fd8b:...::2]" yang membuat httpx LiteLLM gagal total (InvalidURL
  "Invalid port: ':1]'") — launcher mengekspor no_proxy bersih tanpa
  kurung; tes tanpa perbaikan ini gagal sebelum request sampai ke Google.
  Jangan pernah menulis surrogate atau key ke config/log.
- A Groq free-tier key would be the fastest pro brain, but only if the
  user creates it (free account) and orders it.
- Never put an API key, token, password or cookie in a file, env var,
  command argument or log. The Gemini connector key is NOT available to
  this tool (it is a surrogate for the connector only) — do not try to
  extract or reuse it as `GEMINI_API_KEY`.
- Recon tools (subfinder, httpx, nuclei, katana, ffuf, nmap) are
  installed (see Install state above); the CLI works without them.

## Commands

Run from `~/workspace/bughunter/repo` (or any work dir) with the venv CLI:

```bash
~/workspace/bughunter/venv/bin/bughunter help
~/workspace/bughunter/venv/bin/bughunter setup      # choose provider/model
~/workspace/bughunter/venv/bin/bughunter providers  # providers + key status
~/workspace/bughunter/venv/bin/bughunter models     # models for active provider
~/workspace/bughunter/venv/bin/bughunter status     # pipeline status
~/workspace/bughunter/venv/bin/bughunter recon target.com
~/workspace/bughunter/venv/bin/bughunter hunt target.com
~/workspace/bughunter/venv/bin/bughunter validate "finding"
~/workspace/bughunter/venv/bin/bughunter report
~/workspace/bughunter/venv/bin/bughunter chat
```

Short aliases: `h` = hunt, `r` = recon, `v` = validate.
Ollama must be serving first: `curl http://localhost:11434/api/tags` must
respond; if not, start it (`ollama serve`, log
`~/workspace/bughunter/ollama.log`) and check `ollama list` shows `qwen3:4b`.

## Workflow

1. **Scope** — program + in-scope assets confirmed, read program rules.
2. **Recon** — `bughunter recon <target>`, then read
   `skills/web2-recon/SKILL.md` for the pipeline. Ingest leads:
   `bughunter/tools/lead_board.py ingest <target>` + `show`, one lead at
   a time; the board remembers the rest. **Seed the coverage ledger**
   (`targets/<program>/coverage-ledger.json`) from recon: one unit per
   surface × boundary × subsystem × attack class (see the Cloudflare
   adaptation below). Only the parent writes the ledger.
3. **Learn** — read disclosed reports / tech stack for this target before
   hunting (see `skills/bb-methodology/SKILL.md`).
4. **Hunt** — one bug class at a time, deep not sprayed. Route each lead to
   its skill in plain language ("GraphQL endpoint → hunt-graphql"). After
   each wave, run one **coverage-critic** pass (a fresh subagent that only
   checks the ledger for unmapped surfaces); missing units become `planned`
   work. A run closes only when the critic finds no accepted work, or the
   early stop is recorded as `deferred` + disclosed in the report.
5. **Validate** — run the 7-Question Gate (`skills/triage-validation/SKILL.md`)
   BEFORE writing any report. One wrong answer = kill the finding, move on.
   A candidate that passes the gate then goes to a **fresh verifier**
   subagent whose job is to REFUTE it (opposite brain from the hunter:
   Ollama if the hunter used Gemini, Gemini if the hunter used Ollama),
   given only the candidate + its evidence — never the hunter's
   conclusion. Verdict: `confirmed` / `needs_validation` (exact blocker,
   NO severity) / `rejected`. Only `confirmed` may enter a platform
   report. Record all three verdicts in `findings.json` and validate it
   (see below) — a `rejected` record stays so future runs don't repeat
   the same unsupported claim without changed evidence.
6. **Report** — only for findings that pass all 7 questions + the fresh
   verifier + the 4 pre-submission gates. Write them to
   `targets/<program>/findings.json` (3-verdict schema) and run BOTH
   validators before any submission:
   `node ~/workspace/bughunter/cf-adapt/validate-findings.cjs findings.json`
   and `node ~/workspace/bughunter/cf-adapt/validate-coverage-ledger.cjs coverage-ledger.json`.
   Then use `skills/report-writing/SKILL.md` templates, CVSS 3.1, human
   tone, copy-paste-ready PoC.

## Adaptasi Cloudflare security-audit (14 Nov 2026)

Diadaptasi dari `github.com/cloudflare/security-audit-skill` (MIT) atas
perintah pengguna. Kit: `~/workspace/bughunter/cf-adapt/` (validator
`.cjs` TIDAK diubah; `report-schema.json` diadaptasi — lihat
`cf-adapt/README.md` + `adapt-schema.py`). Referensi upstream:
`~/workspace/bughunter/security-audit-ref/`. Detail lengkap + deviasi
tercatat ada di `cf-adapt/README.md`.

Yang diadopsi: (1) **coverage ledger** per target — satu unit per
surface × boundary × subsystem × attack class, status
planned/in_progress/covered/candidate/blocked/deferred/out_of_scope,
`coverage_id` dihitung via `canonicalCoverageId()` validator;
(2) **verifier fresh adversarial** (di atas, langkah 5) — brain
berlawanan, tugasnya menyangkal, bukan mengonfirmasi; (3) **findings.json**
3-verdict (confirmed/needs_validation/rejected) + validator.

Adaptasi skema: trace/evidence boleh pakai lokasi SOURCE (`file`+`line`,
repo-relative) ATAU LIVE (`url` + optional `method`/`request`/`response`)
— satu lokasi per entry. Untuk target black-box, `reviewed_paths` pakai
identifier relatif gaya `api/POST-v1-mint` (validator menolak URL karena
`:`); URL lengkap hanya di field `url` findings.json.

Yang SENGAJA tidak diadopsi: sandbox OS-enforced tanpa network (VM ini
tidak bisa menyediakannya — gantinya: probing live hanya dalam scope
eksplisit, bounded, non-destruktif; PoC source jalan lokal Anvil/fork);
armada multi-agent penuh + budget gate keras (versi ringan: parent +
hunter + verifier + critic, jumlah pemanggilan dicatat); promosi artefak
level file-descriptor (diganti: hanya parent yang menulis
findings.json/ledger; subagent menulis hanya di `agents/<id>/` miliknya).

Bukti dry-run (14 Nov 2026): temuan XE yang sudah difile-kan (XE-9554)
ditulis ulang di `targets/xe/cf-run/` — findings.json 2 valid (C-H1
Medium, C-H2 High, nomor baris asli commit 89a542e, diverifikasi via
clone dangkal) + coverage-ledger.json 6 units valid (5 candidate +
1 covered). Tes upstream: 65/65 pass terhadap skema adaptasi.

## The only question that matters

> "Can an attacker do this RIGHT NOW against a real user who has taken NO
> unusual actions — and does it cause real harm (stolen money, leaked PII,
> account takeover, code execution)?"

If the answer is NO — STOP. Do not write. Do not explore further. Move on.
"Theoretical" is not a bug. "Could" is not a bug. Prove it works or drop it.

## Kill-fast rules

- 5-minute rule: nothing after 5 min probing (all 401/403/404) → move on.
- 1-hour rule: stuck on one target an hour with no progress → switch.
- Kill weak findings fast — N/A hurts the validity ratio; Informative is
  neutral; only submit what passes all 7 questions.
- Don't probe 403s in a loop, don't grep for analytics keys, don't chase
  staging domains that lead nowhere.
- Business impact over vuln class — severity depends on context, not the
  class name. Chains (A→B→C) pay 3–10x single bugs; build the chain first,
  then report one report per chain.

## Reporting back

- Report per target: scope confirmed, recon summary, leads found (with
  status), findings killed with the gate question that killed them,
  findings that passed validation, and the report file path if written.
- Never claim a finding is submitted — submission on HackerOne/Bugcrowd is
  the user's own action unless they explicitly order it, step by step.
- If Ollama is down, the model is missing, or a provider step fails, say
  so plainly with the exact error — do not present a partial run as a
  finished hunt.
