# Verification evidence

Verified 2026-11-23. All documentary examples are synthetic.

## Local contract execution

- **61 tests passed** using `genlayer-test 0.29.2`, Python 3.12 and the real pinned GenLayer SDK in direct mode.
- GenVM AST lint and SDK semantic validation passed: 10 public methods, 6 views and 4 writes.
- GenVM/Pyright type checking passed; ABI schema exported.
- Calldata serialization and nondeterministic closure pickling checks enabled in the main test fixture.

Artifacts: [test output](evidence/tests.txt), [GenVM validation](evidence/genvm-check.txt), [type checking](evidence/typecheck.txt), [schema](evidence/abi.json).

Coverage includes all four outcomes; missing and rejected approvals; exact bundle hashes; account permissions and ordered distinct-account approvals; expiry/age boundaries covering the complete shift; late approval and late assessment; malformed/duplicate/extra JSON; integer/boolean confusion; Unicode byte mismatches; invented model quotations; independent validator disagreement; malformed grounding audits; irreversible stops; immutable receipts; no reapproval/reassessment; and the domain-bound event hash chain.

Direct-mode model outputs are mocked. They test contract enforcement and validator rejection, not model accuracy. `gltest 0.29.2` updates its simulated wall clock on `warp` but leaves the imported `gl.message_raw` timestamp unchanged; the time-advance helper explicitly refreshes that simulated message field before the next call. Production source continues to read the actual transaction timestamp.

## Live Studionet execution

Contract: [0x3911f4e861B48C803829b45f59c7da144580C4BD](https://explorer-studio.genlayer.com/address/0x3911f4e861B48C803829b45f59c7da144580C4BD).

The Studio inbuilt wallet deployed the exact checked source in **Normal (Full Consensus)** mode. The live example locked SHA-256-bound evidence, approved its canonical bundle hash, performed an AI assessment and permanently stopped the permit. The assessment returned **AUTHORIZED** with all four requirements SUPPORTED, then the stop changed the effective result to **VIOLATION** with `may_proceed=false`. The historical assessment remained AUTHORIZED and unchanged.

Machine-readable evidence:

- [Deployment and transaction hashes](evidence/deployment.json)
- [Independent read-only verification](evidence/verified-live.json)
- [Immutable assessment receipt](evidence/assessment-live.json)
- [Effective status after stop](evidence/effective-live.json)
- [Complete event chain](evidence/events-live.json)
- [Locked policy](evidence/policy-live.json)
- [Original live input bundle](evidence/live-input/bundle.json)

The verification script checks finalized transactions, SUCCESS execution, MAJORITY_AGREE, `leader_only=false` and exact deployed-source equality. The separate Python verifier recomputes all event hashes and previous-hash links. Validator votes are exported. Intermediate independent validator findings are not application state and are not represented as separately stored reports.

## Limits

This demonstrates genuine live AI consensus on a synthetic positive case and live stop-work behavior. Local adversarial tests cover additional outcomes with mocks; they are not claimed as live negative-case consensus demonstrations. The demo uses one account with `separate_duties=false`; distinct-account sequencing is tested locally. Account attestations authenticate bytes and accounts, not off-chain issuer signatures or physical safety. Studionet may reset, and this address is not a production safety certification.

Initial Studio requests were temporarily rate-limited; after recovery, deployment and lifecycle execution used full consensus. No leader-only substitute or private-key export was used.
