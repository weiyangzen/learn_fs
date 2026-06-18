<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_block.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_block.rs

## Purpose
Wraps a high-level block and increments shared counters when data is read, data is mutably accessed, or the block is resized.

## APIs, Flow, And State
`TrackingBlock<B>` owns the underlying block and shared `Arc<Mutex<ActionCounts>>`. Public/internal helpers are `new`, `inner_mut`, and `into_inner`. The `Block` implementation forwards `block_id`, increments `blob_data` before `data`, increments `blob_data_mut` before `data_mut`, and increments `blob_resize` before resize.

## Dependencies And Integration
Used as `TrackingBlockStore<B>::Block`. It preserves the underlying block for `remove` and `flush_block` through `into_inner` and `inner_mut`.

## Risks And Test Signals
`block_id` intentionally is not counted. Mutable data access marks the underlying locking cache entry dirty through the wrapped block. Tests cover data, data_mut, resize, remove, and flush paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_block.rs -->
