<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blobstore.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blobstore.rs

## Purpose
Provides a test/testutils blobstore wrapper that records action counts while delegating all storage behavior to an underlying blobstore.

## APIs, Flow, And State
`TrackingBlobStore<B>` owns an `AsyncDropGuard<B>` and shared `Arc<Mutex<BlobStoreActionCounts>>`. Public helpers are `new`, `counts`, and `get_and_reset_counts`. Store methods increment counters then forward to the underlying store; create/load/try_create wrap returned blobs in `TrackingBlob`. Test-only cache clearing and `all_blobs` deliberately pass through without counter fields.

## Dependencies And Integration
Requires the underlying store to implement `BlobStore`, `AsyncDrop`, `Debug`, `Send`, `Sync`, and `'static`. It is re-exported for tests/testutils and used by performance tests and wrapper-specific tests.

## Risks And Test Signals
The wrapper is useful for behavioral cost assertions but can influence scheduling slightly through mutex use. Counter coverage must track trait evolution; newly added trait methods need new fields and tests. Tests verify transparent generic blobstore behavior and exact counts for most methods.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blobstore.rs -->
