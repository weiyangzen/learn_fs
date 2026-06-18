<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/tests.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/tests.rs

## Purpose
Defines blobstore-specific conformance tests and macros for instantiating them.

## APIs, Flow, And State
`instantiate_blobstore_specific_tests!` expands into Tokio tests using the supplied `Fixture`. Currently the `load` module verifies that loading a non-existing blob returns `None` for both empty and non-empty stores. The non-empty case first creates a blob with a fixed ID, then loads a different fixed ID.

## Dependencies And Integration
Uses `Fixture`, `BlobId`, `BlobStore`, `AsyncDrop`, and macro indirection through `_instantiate_blobstore_specific_tests!` so implementations can choose Tokio attributes.

## Risks And Test Signals
The direct blobstore-specific suite is currently sparse; most behavioral coverage comes from the blockstore adapter suite. The TODOs explicitly call for more blobstore-level tests, especially beyond loading non-existing blobs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/tests.rs -->
