# Cloudflare security-audit — adaptasi untuk Agentic Bug Hunter

Sumber: https://github.com/cloudflare/security-audit-skill (MIT).
Klon referensi: `~/workspace/bughunter/security-audit-ref/`
(di-clone 14 Nov 2026; hanya referensi, bukan dependensi).

## Yang dipakai (diadaptasi, bukan disalin mentah)

1. **Coverage ledger** — `coverage-ledger.json` per target di
   `~/workspace/bughunter/targets/<program>/`. Satu unit = kombinasi
   permukaan × boundary × subsistem × kelas serangan. Status persis
   upstream: `planned / in_progress / covered / candidate / blocked /
   deferred / out_of_scope`. Hanya parent (asisten) yang menulis ledger;
   hunter/verifier hanya mengembalikan hasil terstruktur. `coverage_id`
   dihitung dengan `canonicalCoverageId()` dari validator itu sendiri
   (lihat `targets/xe/cf-run/build-ledger.cjs` sebagai contoh).
   Validator: `node validate-coverage-ledger.cjs <ledger>`.
2. **Validasi adversarial (verifier fresh)** — setelah 7-Question Gate
   lolos, kandidat diserahkan ke subagent FRESH yang tugasnya MENYANGKAL
   temuan itu, dengan brain BERLAWANAN (Ollama kalau hunter pakai Gemini,
   Gemini kalau hunter pakai Ollama). Verifier hanya diberi kandidat +
   bukti, bukan kesimpulan hunter. Keputusan: `confirmed` /
   `needs_validation` (blocker persis, TANPA severity) / `rejected`.
   Hanya `confirmed` yang boleh masuk laporan platform.
3. **findings.json (3 verdict) + validator** — `report-schema.json`
   (adaptasi, lihat bawah) + `validate-findings.cjs` (TIDAK diubah).
   Validator membaca skema dari direktorinya sendiri, jadi skema adaptasi
   ini yang dipakai. Semua 65 tes upstream lolos terhadap skema adaptasi
   (`node --test validate-findings.test.cjs validate-coverage-ledger.test.cjs`:
   34 + 31 pass, 14 Nov 2026).

## Adaptasi skema (report-schema.json) — satu-satunya perubahan

Upstream hanya mengenal lokasi SOURCE (`file` + `line`). Untuk target
black-box web, trace/evidence boleh pakai lokasi LIVE (`url` + optional
`method`/`request`/`response`). Satu lokasi per entry (oneOf):
`file+line` ATAU `url`. Kalau satu langkah punya keduanya, tulis dua
entry (satu source, satu live). Skrip adaptasi yang bisa diulang:
`adapt-schema.py` (input = skema upstream, output = skema ini).
Bukti: `sample-blackbox-findings.json` (url-branch, PASS) + kontrol
negatif (entry tanpa lokasi, DITOLAK dengan benar).

## Konvensi path (supaya validator lolos)

- Audit source: `reviewed_paths` / `starting_paths` = path repo-relative
  (`core/quorum.go`). `file` di findings = path yang sama.
- Black-box web: validator menolak URL (`:` dilarang di path). Pakai
  identifier relatif gaya `api/POST-v1-mint` (method + path, tanpa skema,
  tanpa `:`). URL lengkap hanya muncul di field `url` findings.json.
- Artefak bukti lokal: `agents/<agent-id>/artifacts/<file>` di dalam
  direktori run target; hanya parent yang mempromosikan ke sana.

## Yang SENGAJA tidak diadopsi (deviasi tercatat)

- **Sandbox OS-enforced tanpa network**: VM ini tidak bisa
  menyediakannya. Sebagai ganti: probing live HANYA di dalam scope
  eksplisit program, bounded, non-destruktif; PoC source jalan lokal
  (Anvil/fork/harness). Jangan pernah klaim sebuah run "sandboxed".
- **Armada multi-agent penuh + budget gate keras**: dipakai versi
  ringan — parent + hunter + verifier + coverage-critic; jumlah
  pemanggilan subagent dicatat di laporan run; pengguna boleh menetapkan
  budget, tapi tidak ada gate otomatis.
- **Promosi artefak level file-descriptor**: diganti aturan sederhana —
  hanya parent yang menulis `findings.json` / `coverage-ledger.json`;
  subagent menulis hanya di `agents/<id>/` miliknya sendiri.

## Dry-run bukti (14 Nov 2026)

`~/workspace/bughunter/targets/xe/cf-run/` — temuan XE yang sudah
difile-kan (XE-9554) ditulis ulang sebagai findings.json + ledger:
- `findings.json`: **2 findings valid** (xe:C-H1 Medium, xe:C-H2 High).
  Trace memakai nomor baris ASLI dari commit `89a542e` (dicek via clone
  dangkal `targets/xe/xe-src/` — ValidateVote vote.go:225,
  receiveVoteInner vote.go:134, finalTally quorum.go:103,
  confirmConflict quorum.go:263, pickWinner quorum.go:152, dst).
- `coverage-ledger.json`: **6 units valid** (5 candidate + 1 covered).
- Artefak PoC disalin ke `agents/parent/artifacts/`.

## Cara pakai

```sh
cd ~/workspace/bughunter/cf-adapt
node validate-findings.cjs <path>/findings.json
node validate-coverage-ledger.cjs <path>/coverage-ledger.json
node --test validate-findings.test.cjs validate-coverage-ledger.test.cjs
```
