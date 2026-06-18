<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/integrity_violation_error.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/integrity_violation_error.rs

## Purpose
Defines structured errors for integrity violations detected by the low-level integrity blockstore.

## APIs, Flow, And State
`IntegrityViolationError` variants are `RollBack`, `WrongBlockId`, `MissingBlock`, and `MissingBlocks`. Rollback captures the block, source/destination client IDs, last-seen versions, and actual version. Wrong ID records filename/header mismatch. Missing variants record one or many expected block IDs. The enum derives `thiserror::Error`, `Debug`, `PartialEq`, and `Clone`.

## Dependencies And Integration
Uses integrity metadata types `BlockVersion`, `ClientId`, `MaybeClientId`, and crate `BlockId`. These errors are re-exported through the integrity blockstore API and surfaced when tampering, deletion, rename, or rollback is detected.

## Risks And Test Signals
The error messages are security-facing diagnostics and should not lose the block/client/version context needed for incident analysis. `MissingBlocks` owns a `HashSet`, so displayed order is nondeterministic; tests should compare variants structurally rather than strings when possible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/integrity_violation_error.rs -->
