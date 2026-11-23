# Deployment and reproduction

Network: GenLayer Studionet, chain ID **61999**.

Contract: [0x3911f4e861B48C803829b45f59c7da144580C4BD](https://explorer-studio.genlayer.com/address/0x3911f4e861B48C803829b45f59c7da144580C4BD).

Deployment used GenLayer Studio's existing inbuilt wallet, **Normal (Full Consensus)**, without exporting a private key. The deployment and lifecycle transaction list is maintained in [evidence/deployment.json](evidence/deployment.json). The deployed source must match `contracts/permit_gate.py` byte-for-byte.

## Reproduce using Studio

1. Open [GenLayer Studio](https://studio.genlayer.com/contracts). Upload `contracts/permit_gate.py`, then choose Run and Debug.
2. Keep execution mode **Normal (Full Consensus)** and Simulation Mode off. Use the inbuilt Studio wallet.
3. Prepare your own policy from `fixtures/policy.json`; replace operator/approver addresses with controlled accounts. Enable `separate_duties` and use distinct accounts when demonstrating role separation. Do not treat the included single-account synthetic example as independent human approvals.
4. Paste the complete policy JSON into the constructor's `policy_json` field and deploy. Wait for FINALIZED and inspect the execution result for SUCCESS.
5. Generate fresh synthetic dates and evidence with `python scripts/make_fixtures.py YOUR_PUBLIC_ACCOUNT UNIX_NOW`. This writes demonstration fixtures only; it makes no network calls and never requests a secret.
6. As the locked operator, call `lock_permit` with the generated bundle JSON. The script prints the canonical bundle hash. Wait for finalized success.
7. As each ordered approver, call `attest` with the permit ID, exact bundle hash and boolean decision. The single-account demo has one approver. Wait for finalized success after each write.
8. Call `evaluate` as the operator or a designated approver. This invokes live AI consensus. Read `get_receipt` from **Finalized** state. Inspect SUCCESS, MAJORITY_AGREE and full consensus in the transaction details; a transaction hash alone is not proof of completion.
9. Read `effective_status`. Before the work interval, `may_proceed` is false even for AUTHORIZED. Test permanent stop with `stop_work` and verify the effective result becomes VIOLATION while the historical assessment remains unchanged.

The generator's default timestamps are fixed for local tests. A network demonstration must use fresh timestamps, while preserving the original fixtures for reproducible tests. Live input snapshots are kept separately under `evidence/live-input/`.

## Read-only evidence export

```sh
npm ci
npm run verify:live
python scripts/verify_chain.py evidence/events-live.json
```

The exporter does not sign transactions or require a wallet key. It checks remote source identity, finalized full-consensus transaction success and exports the event chain. The Python verifier checks every event hash, sequence, domain and previous-hash link. It does not independently re-run the LLM or prove real-world safety.

Studionet can be rate-limited and reset. If RPC returns HTTP 429, stop rapid requests and wait before a bounded retry. Do not switch to leader-only execution to claim validator verification. If a reset removes this address, redeploy the exact source and record the new address and transaction evidence explicitly.
