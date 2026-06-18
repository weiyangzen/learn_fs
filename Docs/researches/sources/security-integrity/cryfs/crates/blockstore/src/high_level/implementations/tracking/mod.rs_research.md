<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/mod.rs

## Purpose
Module hub for high-level blockstore tracking utilities.

## APIs, Flow, And State
Declares `action_counts`, `tracking_block`, and `tracking_blockstore`, then re-exports `ActionCounts` and `TrackingBlockStore`. Tests are compiled under `cfg(test)`.

## Dependencies And Integration
Enabled only through the parent module's test/testutils gate, making it available for performance and behavior assertions without becoming core production API.

## Risks And Test Signals
Runtime logic lives in child modules. The main risk is incomplete re-exporting when new tracking utilities are added.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/mod.rs -->
