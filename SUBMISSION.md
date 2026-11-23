# GenLayer submission

Category: **Intelligent Contracts** (standalone primitive).

## Title
PermitGate — High-Risk Work Authorization Verification

## Description
PermitGate verifies hazardous-work permit evidence against locked procedures, worker qualifications, equipment checks and ordered approvals. Designated accounts attest the exact SHA-256-bound bundle; independent GenLayer validators re-examine each requirement and audit source quotations. Deterministic rules enforce approval order, work windows and record validity across the full shift, producing AUTHORIZED, CONDITIONAL, VIOLATION or INCONCLUSIVE. Conditional findings never enable work. Hash-linked, domain-bound receipts preserve every lock, approval, assessment and permanent stop. Includes adversarial SDK tests and live Studionet evidence. Verifies documentary compliance without guaranteeing physical safety.

## Evidence

- Repository: https://github.com/haris4587/PermitGate
- Contract explorer: https://explorer-studio.genlayer.com/address/0x3911f4e861B48C803829b45f59c7da144580C4BD
- Source: `contracts/permit_gate.py`
- Deployment/lifecycle: `evidence/deployment.json`
- Final verification: `EVIDENCE.md`
- Security and limitations: `SECURITY.md`

The demonstration is synthetic and uses one Studio account with separation of duties explicitly disabled. Production-style distinct-account approval order is covered in the SDK tests. Submission text describes documentary assessments, not real industrial safety authorization.
