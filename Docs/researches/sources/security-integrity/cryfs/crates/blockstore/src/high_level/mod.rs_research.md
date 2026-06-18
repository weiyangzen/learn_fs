<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/mod.rs

## Purpose
High-level blockstore module root.

## APIs, Flow, And State
Declares `interface` and re-exports `Block`/`BlockStore`; declares `implementations` and re-exports `LockingBlockStore`. Test/testutils re-exports include `ActionCounts`, `SharedBlockStore`, and `TrackingBlockStore`.

## Dependencies And Integration
Feeds the crate root public API and separates high-level block abstractions from low-level storage adapters.

## Risks And Test Signals
No runtime logic is present. Feature-gated re-exports must remain aligned with the parent implementations module.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/mod.rs -->
