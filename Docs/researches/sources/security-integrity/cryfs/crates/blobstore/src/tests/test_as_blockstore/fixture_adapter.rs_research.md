<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/fixture_adapter.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/fixture_adapter.rs

## Purpose
Converts a blobstore `Fixture` into a low-level blockstore `LLFixture` by wrapping created stores in `BlockStoreAdapter`.

## APIs, Flow, And State
`TestFixtureAdapter<F, FLUSH_CACHE_ON_YIELD>` stores the original blobstore fixture. `store` builds the underlying blobstore then returns an adapter. `yield_fixture` optionally clears the adapter/blobstore cache and then calls the original fixture's `yield_fixture` with the inner blobstore.

## Dependencies And Integration
Used by `instantiate_tests_for_blobstore!` to run blockstore tests against blobstores in both flushing and non-flushing modes.

## Risks And Test Signals
The ordering in `yield_fixture` matters: adapter cache clearing occurs before fixture-specific yielding. This surfaces persistence bugs when flushing is enabled while keeping a cached-mode lane for pure behavior tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/fixture_adapter.rs -->
