<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tests.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tests.rs

## Purpose
Tests `TrackingBlobStore` as both a normal blobstore and a counter-instrumented wrapper.

## APIs, Flow, And State
`TestFixture` wraps `BlobStoreOnBlocks<LockingBlockStore<InMemoryBlockStore>>` in `TrackingBlobStore` and runs `instantiate_tests_for_blobstore!`. Counter tests then create/load/remove blobs, call every blob method, call store metadata methods, collect `all_blocks` streams, and assert exact `BlobStoreActionCounts` snapshots. `change_blob_id` produces a non-existing ID by mutating the first byte.

## Dependencies And Integration
Uses the public blobstore traits, the tracking wrapper, `RemoveResult`, `futures::StreamExt`, and `pretty_assertions`. It reaches `tracking_blob::TrackingBlob` to test the associated `remove` path directly.

## Risks And Test Signals
The test suite is a detailed signal that tracking remains transparent and complete. It checks counters increase on success and on not-found cases for store operations. It does not exercise poisoned mutex handling or very high counter values, and `store_flush_if_cached` is present in the counter type but not covered in the visible counter tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tests.rs -->
