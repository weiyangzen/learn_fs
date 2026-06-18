<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_blockstore.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_blockstore.rs

## Purpose
Provides a high-level blockstore wrapper that records action counts while preserving the underlying store's behavior.

## APIs, Flow, And State
`TrackingBlockStore<B>` owns an `AsyncDropGuard<B>` and shared `Arc<Mutex<ActionCounts>>`. `counts` snapshots counters, and `get_and_reset_counts` atomically replaces them with `ZERO`. Most store methods increment before forwarding; `create` increments after successful underlying create, so failed creates are not counted. Loaded blocks are wrapped in `TrackingBlock`. `remove` unwraps the tracking block via `into_inner`; `flush_block` forwards a mutable reference to the underlying block through `inner_mut`.

## Dependencies And Integration
Generic over high-level `BlockStore + AsyncDrop + Debug + Send + Sync`, with blocks that are `Send + Sync`. Test/testutils cache clearing passes through uncounted.

## Risks And Test Signals
Counting after successful `create` differs from methods that count attempts, which matters for interpreting metrics. The mutex is not held across awaited calls except for quick increments. Tests cover counters, generic behavior, and reset.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_blockstore.rs -->
