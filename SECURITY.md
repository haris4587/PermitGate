# Security and limitations

PermitGate verifies documentary compliance. It does not certify physical safety, issue regulatory approvals, operate machinery, verify medical fitness, or replace qualified site personnel. `may_proceed` is an application flag, not a safety interlock.

## Authority and authenticity

The deployer locks organizational policy once. Only its named operator may submit evidence. Ordered approvers must sign the complete bundle hash on-chain. These account attestations authenticate who submitted/approved the bytes; they do not cryptographically validate off-chain signatures, training-provider accreditation, equipment condition, or document truth. Approvers are the organization's trust anchors and must verify original source records. Stolen keys or colluding authorities can attest false evidence. `separate_duties=true` enforces distinct operator/approver accounts, but cannot establish independent human identities. Demo fixtures disable this flag explicitly.

The owner has stop authority even when separate duties is enabled; it cannot rewrite evidence, provide another account's approval or change an assessment. Operator and every approver can stop an unsafe workflow without waiting for an LLM.

## Consensus

Leader and validators use the same immutable evidence. A validator re-runs the substantive assessment, compares every requirement status, then audits quotation meaning against full context. Literal quotation membership is checked deterministically. This prevents a schema-only validator but does not eliminate common model errors, prompt injection or consensus failures. Data is explicitly separated from evaluation instructions; no model output is executed. Local adversarial mocks test enforcement and rejection paths, not resistance of every model to every injection.

Malformed model output produces UNKNOWN; a validator failure rejects the result. Failed consensus does not produce an application receipt and cannot authorize work. There is one assessment per permit with no in-contract re-roll or overwrite. Network appeals remain protocol functionality. A new permit ID cannot conceal the old chain, but detection of real-world duplicate tasks is an organizational responsibility.

## Deterministic checks

Strict input shapes, duplicate-key rejection, UTF-8 SHA-256 and byte counts, bounded canonical sizes, integer timestamps, scope identity, core critical categories and exact record ordering are enforced. Approvals must precede work start and occur in the locked order. Record expiry and maximum age must cover the entire work period. All committed events include contract/chain domain separation. There are no external URL fetches, SSRF, file reads, dynamic evaluation, asset transfers or user-specified model endpoints.

Document dates and named subjects are also compared semantically with the inline record text; deterministic timestamps alone do not prove documentary authenticity. The strongest outcome depends on both checks.

## Lifecycle and time

Receipts are immutable historical findings. Always use `effective_status` at the point of use, from finalized chain state and a node with a current transaction timestamp. A cached receipt cannot establish present authorization. CONDITIONAL never sets `may_proceed`. Stop revocation is permanent; it does not rewrite prior history. No receipt is valid beyond its work end.

Finality is required before acting on results. A stale RPC, replayed response or chain reset can invalidate application assumptions. Studionet is a development network; its data and availability are not production guarantees. Evidence and worker identifiers are public on-chain: use synthetic/redacted records, never confidential training, medical or personnel documents.

## Reporting

Report reproducible security problems through the repository's GitHub issue tracker, without credentials, personal records or real operational permit data. This project has no independent security audit or production safety certification.
