<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tests.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tests.rs

## Purpose
Tests high-level `TrackingBlockStore` transparency and exact counter behavior.

## APIs, Flow, And State
The fixture wraps `LockingBlockStore<InMemoryBlockStore>` and runs the generic high-level suite in flushing and non-flushing modes. Individual tests assert counters for load, overwrite, remove by ID, remove by loaded block, try-create success/failure, create, block resize, flush, data/data_mut access, block count, free-space estimate, overhead calls, all_blocks stream creation, and `get_and_reset_counts`.

## Dependencies And Integration
Uses high-level `Block`/`BlockStore` traits, `Data`, `BlockId`, `Byte`, futures stream collection, and `pretty_assertions`. It exercises the tracking wrapper on top of the real locking store rather than a mock.

## Risks And Test Signals
The tests are detailed instrumentation signals but mostly sequential; they do not stress concurrent counter updates beyond generic multi-thread execution. The aggregate reset test verifies that counters can be accumulated across mixed operations and reset to zero.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tests.rs -->
