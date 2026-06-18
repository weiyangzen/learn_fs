<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/action_counts.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/action_counts.rs

## Purpose
Defines `BlobStoreActionCounts`, the counter set used by the blobstore tracking wrapper to record which blob and store APIs were invoked.

## APIs, Flow, And State
The struct contains `u32` counters for blob operations (`num_bytes`, `resize`, reads, writes, flush, node count, remove, all_blocks) and store operations (`create`, `try_create`, `load`, remove, node count, capacity/block-size queries, flush-if-cached). `derive_more` provides addition, add-assign, and sum, and `ZERO` is a constant all-zero baseline. Custom `Debug` omits zero-valued fields for readable assertions.

## Dependencies And Integration
Used by `TrackingBlobStore` and `TrackingBlob` behind an `Arc<Mutex<_>>`. The type is exported under test/testutils from the crate root.

## Risks And Test Signals
Counters are `u32`, so extremely long-running instrumentation could overflow in debug or wrap in release if not guarded by Rust overflow settings. The explicit custom `Debug` must be updated when fields are added. Tracking tests verify zero state, each counter increment, and reset behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/action_counts.rs -->
