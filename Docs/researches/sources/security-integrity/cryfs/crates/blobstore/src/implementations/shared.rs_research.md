<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/shared.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/shared.rs

## Purpose
Implements `BlobStore` for `AsyncDropArc<B>`, allowing a blobstore to be shared while retaining the same async-drop and trait behavior.

## APIs, Flow, And State
Every `BlobStore` method delegates through `Deref` to the underlying store: create/load/remove, size/capacity queries, cache flushing, test cache clearing, and test-only `all_blobs`. The concrete blob type is unchanged (`B::ConcreteBlob`), so sharing does not wrap individual blobs.

## Dependencies And Integration
Depends on `cryfs_utils::async_drop::{AsyncDrop, AsyncDropArc, AsyncDropGuard}` and the blobstore interface. Its tests wrap `BlobStoreOnBlocks<LockingBlockStore<InMemoryBlockStore>>` in `AsyncDropArc` and instantiate the full blobstore suite.

## Risks And Test Signals
The wrapper is intentionally transparent; risks are missed delegation when the trait grows, or shared lifetime/drop behavior diverging from a direct store. The generic tests verify functional equivalence under a shared wrapper but do not stress concurrent clones beyond normal multi-thread Tokio execution.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/shared.rs -->
