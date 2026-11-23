# PermitGate

**High-risk work authorization verification using a standalone GenLayer Intelligent Contract.**

PermitGate compares a locked work permit against an organization's immutable procedure, approval order, worker qualifications and equipment checks. Independent validators interpret documentary evidence; deterministic code controls permissions, record validity, work intervals and the final assessment. It assesses documentary compliance, not physical workplace safety.

## Workflow

1. Deploy `contracts/permit_gate.py` with `policy_json`. The policy fixes site, task type, procedure, named requirement subjects, criticality, operator, ordered approver accounts and validity limits. No policy setter or upgrade mechanism exists.
2. The designated operator calls `lock_permit(bundle_json)` before work starts. The complete evidence text is stored immutably with its SHA-256 and exact UTF-8 byte count. Each requirement has an ordered record containing issue/expiry Unix seconds.
3. Each designated approver calls `attest(permit_id, bundle_hash, approved)` in the locked sequence. The contract authenticates the caller and binds the decision to the exact canonical bundle. Decisions cannot be overwritten.
4. The operator or a designated approver calls `evaluate(permit_id)`. The leader reviews each requirement and supplies source quotations. Validators independently repeat the analysis, compare every requirement status and audit the leader's quotations against the full evidence. Deterministic rules derive the outcome.
5. Read `get_receipt` and `effective_status`. A receipt is a historical assessment. `may_proceed` is true only for an AUTHORIZED assessment inside its work interval without a stop. CONDITIONAL never permits work.
6. Owner, operator or any locked approver can call `stop_work` before or after evaluation. A stop is irreversible and immediately disables the effective authorization. Historical receipts remain unchanged.

## Outcomes

Precedence is **VIOLATION → INCONCLUSIVE → CONDITIONAL → AUTHORIZED**.

| Outcome | Rule |
|---|---|
| AUTHORIZED | Every requirement is SUPPORTED, all approvals are affirmative, every record covers the full work period, and assessment occurs before work starts. |
| CONDITIONAL | All critical requirements are SUPPORTED, but an explicitly advisory requirement is CONTRADICTED. No work permission is granted. |
| VIOLATION | A critical requirement is CONTRADICTED, an approval is rejected, record validity fails, or authorization is attempted at/after work start. A stopped or expired permit also has an effective VIOLATION status. |
| INCONCLUSIVE | Missing approval or UNKNOWN evidence, with no higher-priority violation. Malformed model output is normalized to UNKNOWN. Consensus failure leaves the transaction uncommitted and grants no permission. |

A failed advisory record's deterministic validity check still produces VIOLATION. Core procedure, qualification and equipment categories must each contain a critical requirement. AUTHORIZED before the work start is an assessment only: `may_proceed` remains false until the start time. A pre-work stop remains effective even without a receipt.

## Why GenLayer

The difficult step is interpreting whether reports substantiate the specific procedure and named subjects, whether limitations or negations invalidate an apparent pass, and whether submitted dates match documentary dates. This uses real `gl.nondet.exec_prompt` inside `gl.vm.run_nondet_unsafe`, with an independent validator extraction and a separate quotation audit. Validators do not approve a leader merely for returning valid JSON.

Evidence is supplied inline, not fetched from mutable websites. This avoids redirects, SSRF and changing external files. A hash binds bytes; transaction signatures establish which accounts attested those bytes. Neither proves the records are truthful or that an off-chain signature belongs to an accredited issuer. Organizations must designate suitable approver accounts and authenticate source records before attesting.

## Run verification

Python 3.12 and network access for official GenVM artifacts are required on first run.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
genvm-lint check contracts/permit_gate.py
genvm-lint typecheck contracts/permit_gate.py
genvm-lint schema --json contracts/permit_gate.py
```

The tests execute the contract through the official GenLayer direct SDK with calldata and nondeterministic closure serialization checks. LLM answers are mocked; local tests do not establish live model accuracy or network consensus. See [EVIDENCE.md](EVIDENCE.md) for the separate live verification record.

## API

Constructor: `PermitGate(policy_json: str)`.

| Write method | Caller / effect |
|---|---|
| `lock_permit(bundle_json)` | Locked operator; new immutable permit ID. |
| `attest(permit_id, bundle_hash, approved)` | Next locked approver; approve/reject the exact bundle. |
| `evaluate(permit_id)` | Operator/approver; exactly one assessment per permit. |
| `stop_work(permit_id, reason)` | Owner/operator/approver; permanent stop. |

Views: `get_policy()`, `get_permit(permit_id)`, `get_receipt(permit_id)`, `get_event(sequence)`, `get_status()`, `effective_status(permit_id)`. All return JSON strings. Event sequence is one-based. Every lock, attestation, assessment and stop extends a domain-bound SHA-256 chain.

See [fixtures/policy.json](fixtures/policy.json) and [fixtures/bundle.json](fixtures/bundle.json) for exact schemas. JSON rejects unknown/duplicate keys, booleans as integers, out-of-range timestamps, duplicate requirement IDs and incorrect record ordering. All times are UTC Unix seconds. Expiry equal to `work_end` is valid; effective authorization expires at `now >= work_end`.

Limits: 12 requirements, 6 approvals, 16,000 evidence bytes, 24,000 bundle JSON bytes, 18,000 policy JSON bytes, 8–800 character quotations, a maximum 24-hour work duration and seven-day scheduling horizon. Canonical escaped storage sizes are bounded too.

## Receipts and trust boundaries

Canonical JSON uses sorted keys, compact separators and ASCII escaping. `bundle_hash = SHA256(canonical(bundle))`; evidence hashes cover the exact UTF-8 evidence bytes. Event hashes cover the entire event except `event_hash`, including contract address, chain ID, actor, sequence, previous hash, policy hash and payload. Export the full event chain and run:

```sh
python scripts/verify_chain.py evidence/events-live.json
```

Changing a policy or replacing evidence requires a new deployment/permit. There is no delete, evidence rewrite, retry-to-favorable-result or stop reversal. A new permit does not erase earlier assessments; organizations must track task identity and refuse duplicate real-world work authorizations themselves.

**Demo scope:** Included data is synthetic. Its single account holds multiple roles and `separate_duties` is false, explicitly for demonstrating the Studio wallet flow. Enable `separate_duties` and supply distinct operator/approver accounts for organizational separation. The owner can always stop work, but cannot edit policy or force an AUTHORIZED result.

[Deployment](DEPLOYMENT.md) · [Security](SECURITY.md) · [Evidence](EVIDENCE.md) · [Submission](SUBMISSION.md) · [MIT license](LICENSE)

## Official references

- [Equivalence Principle and independent validators](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- [Transaction context and timestamps](https://docs.genlayer.com/developers/intelligent-contracts/features/transaction-context)
- [Non-deterministic execution](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism)
- [GenVM linter](https://github.com/genlayerlabs/genvm-linter)
- [GenLayer testing](https://docs.genlayer.com/developers/intelligent-contracts/testing)

References checked on 2026-11-23. The source pins the runner used by Studio rather than relying on an unpinned latest runtime.
