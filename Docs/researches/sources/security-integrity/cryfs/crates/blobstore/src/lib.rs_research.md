<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/lib.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/lib.rs

## Purpose
Crate root for `cryfs_blobstore`, wiring public blobstore identity, traits, implementations, test utilities, and version checks.

## APIs, Flow, And State
The crate forbids unsafe code, defines `blob_id`, `interface`, and `implementations`, and re-exports `BlobId`, `Blob`, `BlobStore`, `BLOBID_LEN`, `BlobOnBlocks`, `BlobStoreOnBlocks`, data-node/tree types, and `RemoveResult`. Under test/testutils it also re-exports `BlobStoreActionCounts` and `TrackingBlobStore`.

## Dependencies And Integration
Depends publicly on `cryfs_blockstore::RemoveResult` and `cryfs_version::assert_cargo_version_equals_git_version!()`. The test module is only compiled under `cfg(test)`.

## Risks And Test Signals
This file controls public API surface and feature-gated test helpers. The version assertion guards release consistency. Since missing docs are only a TODO, API documentation completeness is not currently enforced.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/lib.rs -->
