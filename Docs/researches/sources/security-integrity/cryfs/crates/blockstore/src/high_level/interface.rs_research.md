<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/interface.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/interface.rs

## Purpose
Defines the high-level block and blockstore traits used by cache-aware blockstore implementations.

## APIs, Flow, And State
`Block` exposes `block_id`, immutable/mutable `Data`, and async resize. `BlockStore` exposes load, try-create, overwrite, remove by ID, remove by loaded block, count/free-space/overhead queries, `all_blocks`, random-ID create, flush of a loaded block, and test/testutils cache clearing. Stream methods explicitly do not guarantee a consistent snapshot during concurrent mutations.

## Dependencies And Integration
High-level stores sit above low-level `LLBlockStore` implementations and below blobstore data-tree code. The trait uses `BlockId`, `Overhead`, `RemoveResult`, `TryCreateResult`, `Byte`, `Data`, and boxed futures streams.

## Risks And Test Signals
The trait allows mutable block handles to carry dirty state that must be flushed by store implementations. Comments note a future migration opportunity away from direct `LockingBlockStore` use. Generic high-level blockstore tests validate implementors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/interface.rs -->
