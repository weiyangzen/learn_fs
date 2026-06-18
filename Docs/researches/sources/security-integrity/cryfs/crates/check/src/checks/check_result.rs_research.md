# sources/security-integrity/cryfs/crates/check/src/checks/check_result.rs

Purpose: `CheckResult` is the accumulation object for checker errors and internal assertions.

Important APIs and flow: It stores `errors: Vec<CorruptedError>` and `assertions: Vec<Assertion>`. `add_error`, `add_assertion`, and `add_all` merge outputs from individual checks. `peek_errors` allows invariant checks before final ownership is consumed. `finalize` validates every assertion against the final error vector, then returns errors.

State and persistence: All state is in-memory during one checker run. No deduplication is performed here; checks are responsible for deterministic aggregation before adding errors.

Dependencies and integration: It is used by individual `FilesystemCheck` implementations and by `AllChecks::finalize`. The assertion link makes algorithmic self-tests part of normal result finalization.

Risks and test signals: Because assertion validation can panic, a missing correlated error becomes a checker bug rather than a reported corruption. This is useful during development but could be harsh in production for unanticipated corruptions.
