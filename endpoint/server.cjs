// Agentic Bug Hunter — public demo endpoint.
// Node.js, zero dependencies. Serves the agent card, health, and a
// redacted sample report. Read-only: it never runs scans on demand.
// Run: node server.cjs [port]   (default 8080, binds 127.0.0.1)
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.argv[2] || 8080);
const HOST = '127.0.0.1';
const STARTED = Date.now();

const AGENT_CARD = {
  name: 'Agentic Bug Hunter',
  tagline: 'A security agent that hunts vulnerabilities in smart contracts and protocols, with machine-checkable findings.',
  version: '1.0.0',
  competition: 'zkVerify Agent Games — Wildcard track',
  repository: 'https://github.com/icallshelby/bughunter-agent',
  who_it_helps: 'Bug-bounty hunters and protocol teams who need real, verified findings instead of AI hallucinations.',
  how_it_works: [
    'Scope-first: only hunts targets with an explicit program and scope.',
    'Recon: subfinder, httpx, nuclei, katana, amass, gau and friends map the target.',
    'Hunt: an AI brain (Gemini via LiteLLM, Ollama fallback) reads code and proposes findings.',
    '7-Question Gate: every candidate must survive seven validation questions before it counts.',
    'Adversarial verifier: a second, independent reviewer tries to REFUTE each finding; only confirmed findings ship.',
    'Validators: deterministic Node validators check findings.json and the coverage ledger before any submission.',
  ],
  key_decisions: [
    'Free-only: no paid filing, no paid tooling, no paid model required.',
    'Evidence over claims: a finding without a reproduction is not a finding.',
    'Verification is a separate seat from hunting — the hunter never grades its own work.',
  ],
  endpoints: ['GET /', 'GET /health', 'GET /report'],
  zkverify_note: 'No zkVerify integration is shipped yet. Findings are already machine-checkable claims (schema + validator verdicts); making a validator verdict provable on-chain via zkVerify is the natural next step, not a claimed feature.',
};

function sendJson(res, status, obj) {
  const body = JSON.stringify(obj, null, 2);
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  res.end(body);
}

function sendText(res, status, text) {
  res.writeHead(status, { 'content-type': 'text/plain; charset=utf-8' });
  res.end(text);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  if (req.method === 'GET' && url.pathname === '/') return sendJson(res, 200, AGENT_CARD);
  if (req.method === 'GET' && url.pathname === '/health') {
    return sendJson(res, 200, { status: 'ok', uptime_seconds: Math.floor((Date.now() - STARTED) / 1000) });
  }
  if (req.method === 'GET' && url.pathname === '/report') {
    try {
      const data = fs.readFileSync(path.join(__dirname, '..', 'evidence', 'xe-9554-summary.json'), 'utf8');
      return sendJson(res, 200, JSON.parse(data));
    } catch (e) {
      return sendJson(res, 500, { error: 'sample report unavailable' });
    }
  }
  return sendText(res, 404, 'not found\n');
});

server.listen(PORT, HOST, () => {
  console.log(`bughunter-agent endpoint listening on http://${HOST}:${PORT}`);
});
