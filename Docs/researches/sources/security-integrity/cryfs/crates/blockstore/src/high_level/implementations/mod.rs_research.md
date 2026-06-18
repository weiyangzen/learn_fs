<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/mod.rs

## Purpose
Collects high-level blockstore implementations and feature-gated test utility wrappers.

## APIs, Flow, And State
Always declares/re-exports `locking::LockingBlockStore`. Under test/testutils it declares and re-exports `tracking::{ActionCounts, TrackingBlockStore}` and `shared::SharedBlockStore`.

## Dependencies And Integration
Consumed by `high_level::mod.rs` and crate-root re-exports. This is the visibility gate separating production implementation from test instrumentation/shared wrappers.

## Risks And Test Signals
The module is simple but controls public API exposure. Incorrect feature gating could leak test utilities into production or hide them from downstream test crates.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/mod.rs -->
