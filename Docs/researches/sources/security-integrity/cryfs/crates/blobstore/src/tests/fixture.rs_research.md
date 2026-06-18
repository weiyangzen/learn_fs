<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/fixture.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/fixture.rs

## Purpose
Defines the generic fixture trait used to instantiate the blobstore conformance tests for many implementations.

## APIs, Flow, And State
`Fixture` has an associated `ConcreteBlobStore` constrained to `BlobStore + Debug + AsyncDrop<Error = anyhow::Error> + Send + Sync + 'static`. Implementors provide `new`, async `store`, and `yield_fixture`. The fixture is kept alive for the whole test so it can own temporary directories or other RAII resources.

## Dependencies And Integration
Used by `instantiate_tests_for_blobstore!`, implementation-specific fixtures, tracking tests, shared wrapper tests, and the adapter that runs blockstore tests against blobstores.

## Risks And Test Signals
`yield_fixture` is the key hook for forcing flushes or other persistence transitions between test operations. If a fixture leaves it as a no-op, only cached behavior may be tested for stores that require explicit cache clearing.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/fixture.rs -->
