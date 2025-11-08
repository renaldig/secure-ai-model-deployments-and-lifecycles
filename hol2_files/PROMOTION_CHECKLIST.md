# Promotion Checklist — <service/model name>  (version: <vX.Y.Z>)

> Purpose: A one-minute, objective gate for moving from **Staging → Production**.

## 0) Artifact Identity (must match pipeline output)
- Image/Model URI (immutable): `<registry/repo@sha256:...>` or `<s3://bucket/key>`
- Build commit: `<git SHA>`
- Build timestamp (UTC): `<YYYY-MM-DDTHH:mm:ssZ>`
- Signature: `<Signer profile ARN>` • Verification: `PASS | FAIL` • Evidence: `<link to signature.json>`
- SBOM reference: `<link to sbom.json>` • Inspector summary: `0 CRITICAL` (attach or link)

## 1) Accuracy / Quality (thresholded)
- Primary metric: `<e.g., ROC-AUC 0.93 (>= 0.90)>`
- Secondary: `<e.g., p95 latency ≤ 550ms under N RPS>`
- Evaluation dataset/version: `<name @ hash/URL>`
- Evidence links: `<eval_report.md>`, `<metrics.csv>`

## 2) Safety & Bias (thresholded)
- Unsafe output rate: `<≤ 5%>`  | Prompt restrictions tested: `Yes/No`
- Sensitive categories tested (list): `<PII, toxicity, etc.>`
- Bias slice deltas within limits: `Yes/No`  (attach table or link)
- Evidence links: `<safety_report.md>`, `<bias_report.md>`

## 3) Reproducibility
- Training/inference command (exact, with seed):
- seed=42 python train.py --config configs/prod.yaml
- Data snapshot / lineage: `<dataset name @ commit/hash>`
- Environment: `<container image digest / runtime versions>`
- Evidence links: `<training_log.txt>`, `<config file>`

## 4) Integrity & Supply Chain
- Signature verified (Signer): `Yes/No`  (link to pipeline verification step)
- SBOM generated & scanned: `Yes/No`  (0 CRITICAL findings required)
- Waivers (if any): `<ID, scope, expiry date>`

## 5) Rollback Readiness
- Instant rollback path: `<alias prod → 100% baseline>` (tested on `<date>`)
- Safe flags defaults (if applicable): `SAFE_MODE=on`, `THRESHOLD=<value>`
- Canary plan (if used): `10% → 25% → 50% → 100%` with checks at each step

## 6) Approvals (required)
- **Model Owner**: `<name> <email>` • Decision: `APPROVE / REJECT` • Date: `<…>`
- **Independent Reviewer**: `<name> <email>` • Decision: `APPROVE / REJECT` • Date: `<…>`
- **Platform/SRE**: `<name> <email>` • Decision: `APPROVE / REJECT` • Date: `<…>`

## 7) Release Decision (one line)
- ✅ **PROMOTE** / ❌ **BLOCK** — Because: `<short reason>`  
Evidence bundle: `<folder or PR link>`

---

### PR Template (optional; paste into `.github/pull_request_template.md`)
- [ ] Artifact digest matches pipeline output
- [ ] Signature **verified** (attach signature.json)
- [ ] SBOM **present** and **0 CRITICAL** findings
- [ ] Metrics meet thresholds (link report)
- [ ] Safety/bias checks passed (link report)
- [ ] Rollback plan & flags documented
- [ ] Approvals from Owner, Independent Reviewer, Platform/SRE
