<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/mod.rs

## Purpose
Collects blobstore test modules and defines the top-level macro that applies the full test suite to a blobstore implementation.

## APIs, Flow, And State
`instantiate_tests_for_blobstore!` creates two test modules: `as_blobstore`, using blobstore-specific tests, and `as_blockstore`, using `cryfs_blockstore::instantiate_blockstore_tests_for_lowlevel_blockstore!` through `TestFixtureAdapter` with flushing enabled and disabled.

## Dependencies And Integration
Bridges blobstore testing to the low-level blockstore test suite, treating each blob as a block through `test_as_blockstore`. The macro accepts optional Tokio test arguments, commonly `(flavor = "multi_thread")`.

## Risks And Test Signals
This macro is the main source of cross-interface regression coverage. It also means blobstores must satisfy blockstore-like semantics through the adapter, so failures can indicate adapter assumptions as well as implementation bugs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/mod.rs -->
