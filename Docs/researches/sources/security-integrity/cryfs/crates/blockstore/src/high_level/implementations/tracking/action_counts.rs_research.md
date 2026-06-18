<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/action_counts.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/action_counts.rs

## Purpose
Defines high-level blockstore action counters for the test/testutils tracking wrapper.

## APIs, Flow, And State
`ActionCounts` tracks store operations (`load`, `try_create`, `overwrite`, removals, counts, free-space, overhead, all_blocks, create, flush_block) and block operations (`data`, `data_mut`, `resize`, named `blob_*` in the struct). It derives addition/add-assign/sum/equality/copy and provides `ZERO`. Custom `Debug` prints only non-zero fields.

## Dependencies And Integration
Used by `TrackingBlockStore` and `TrackingBlock` behind `Arc<Mutex<_>>`. Re-exported under test/testutils as `HLActionCounts` from the crate root.

## Risks And Test Signals
Field names use `blob_` for block-level actions, which can confuse readers because this is the blockstore crate. Tests verify zero state, each counter, and reset aggregation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/action_counts.rs -->
