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
