<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/mod.rs

## Purpose
Collects the blobstore tracking implementation and exposes the public test utility types.

## APIs, Flow, And State
The module owns `action_counts`, `tracking_blob`, and `tracking_blobstore`, and re-exports `BlobStoreActionCounts` plus `TrackingBlobStore`. `tracking_blob` remains internal except where tests reach into it from the child test module.

## Dependencies And Integration
The parent `implementations` module re-exports these types only under `test` or `feature = "testutils"`, so production builds are not coupled to tracking wrappers.

## Risks And Test Signals
The module has little logic itself; risks are visibility drift or forgetting to expose new tracking utilities behind the intended feature gates. Its `tests` child exercises the full wrapper behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/mod.rs -->
