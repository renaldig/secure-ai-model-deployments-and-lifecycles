# Signed-Release Gate (Policy Spec)

**Goal:** Block unsafe releases by requiring cryptographic provenance and clean dependency health.

## Required Predicates (all must pass)
1. `signature_valid == true` — Image digest is signed by the trusted profile and verification succeeded.
2. `critical_vulns == 0` — Amazon Inspector (SBOM-based) reports **zero CRITICAL** findings for this image digest.
3. `evidence_present == true` — Links to `signature.json` and `sbom.json` (or Inspector finding view) are attached.

## Inputs
- `digest`: `sha256:<...>`
- `signature.json`: `{ "imageRef": "<repo@sha256:...>", "signatureVerified": true|false }`
- `sbom.json` or Inspector result: count of CRITICAL findings for `<digest>`

## Pass / Fail Messages
- **PASS:** `Release allowed: signature OK, 0 CRITICAL findings for <digest>.`
- **FAIL (signature):** `Blocked: missing/invalid signature for <digest>.`
- **FAIL (vulns):** `Blocked: <N> CRITICAL vulnerabilities for <digest>.`
- **FAIL (evidence):** `Blocked: evidence links missing (signature/SBOM).`

## Emergency Waiver Process (time-boxed)
- Waiver record in repo: `waivers/<digest>.md` with:
  - Owner, scope (exact digest), reason, compensating controls, **expiry date** (≤ 7 days).
- Pipeline reads waiver; **only** permits deploy when:
  - `signature_valid == true` **and** `critical_vulns` are **acknowledged** with compensating control.
- Post-condition: track Jira `<ID>` to remove waiver; rebuild/re-sign image before expiry.

## References
- Signing profile: `<arn:aws:signer:region:acct:signing-profile/prod-artifacts>`
- ECR repo: `<account>.dkr.ecr.<region>.amazonaws.com/<repo>`
- Example evidence: `signature.json`, `sbom.json`
