# Model Card — <model name>  (version: <vX.Y.Z>)

## Intended Use
- Primary task: `<classification / ranking / generation …>`
- Supported inputs/outputs: `<text in EN> → <label {positive,negative}>`
- Users & context: `<checkout scoring service, internal API>`

## Limitations
- Known weaknesses: `<short text>`
- Not for: `<domains, languages, populations>`

## Data & Training
- Data sources & license: `<SST-2 @ commit; license ref>`
- Preprocessing: `<lowercasing, tokenization>`
- Training config: `<epochs, batch size, lr, seed=42>`
- Model base: `<distilbert-base-uncased @ digest>`

## Evaluation (summary)
- Primary metric: `<ROC-AUC 0.93>` on `<dataset split>`
- Latency (p95 @ N RPS): `<540ms>`
- Failure modes observed: `<outliers on very long inputs>`

## Safety & Bias
- Safety tests: `<PII redaction, toxicity guards>` — result: `<within limits>`
- Bias slices: `<delta ≤ 3% across slices>` — link table: `<…>`
- UnsafeOutputRate: `<≤ 5%>` — methodology: `<…>`

## Monitoring Watch-Points
- **LatencyMs p95** threshold: `≤ 500 ms` (alarm: clamp traffic)
- **UnsafeOutputRate** threshold: `≤ 5%` (alarm: immediate rollback)
- Logging tags: `version_tag`, `alias`, `build_digest`

## Operational Notes
- Rollback plan: `<alias prod → 100% baseline; SAFE_MODE=on>`
- Config flags: `SAFE_MODE`, `THRESHOLD`
- Contact / DRI: `<name, channel>`

## References
- Checklist: `PROMOTION_CHECKLIST.md`
- SBOM: `<link>`
- Signature evidence: `<link to signature.json>`
- Evaluations: `<link>`
