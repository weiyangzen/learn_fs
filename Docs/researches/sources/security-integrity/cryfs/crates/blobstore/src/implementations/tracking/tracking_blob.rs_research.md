<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blob.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blob.rs

## Purpose
Wraps a concrete blob and increments shared action counters before forwarding all `Blob` operations.

## APIs, Flow, And State
`TrackingBlob<B>` stores an `AsyncDropGuard<B::ConcreteBlob>` plus `Arc<Mutex<BlobStoreActionCounts>>`. `new` returns an `AsyncDropGuard<Self>`. Trait methods increment the corresponding counter and delegate to the underlying blob. `remove` consumes the tracking guard with `unsafe_into_inner_dont_drop`, increments `blob_remove`, and calls the underlying concrete blob's associated `remove`.

## Dependencies And Integration
Generic over a `BlobStore + AsyncDrop + Debug + 'static`; used exclusively by `TrackingBlobStore` as its `ConcreteBlob`. It forwards `all_blocks` as a boxed stream of `BlockId` and forwards async drop to the wrapped blob.

## Risks And Test Signals
The mutex lock is held only for the increment, avoiding holding it across awaited underlying calls. The `remove` path is more delicate because it manually unwraps the async-drop guard to transfer ownership. Tests cover every counter path, including `TrackingBlob::remove`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blob.rs -->
