<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/mod.rs

## Purpose
Small module that exposes the blobstore-as-blockstore fixture adapter.

## APIs, Flow, And State
Declares `block_store_adapter` and `fixture_adapter`, and publicly re-exports `TestFixtureAdapter`. No runtime state lives here.

## Dependencies And Integration
Imported by the top-level test macro to instantiate low-level blockstore tests for blobstore implementations.

## Risks And Test Signals
The only risk is module visibility drift. Functional coverage lives in the adapter and in the generic tests that consume it.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/mod.rs -->
