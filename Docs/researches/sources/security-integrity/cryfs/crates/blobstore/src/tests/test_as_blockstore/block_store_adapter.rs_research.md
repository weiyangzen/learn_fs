<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/block_store_adapter.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/block_store_adapter.rs

## Purpose
Adapts any `BlobStore` into a low-level `LLBlockStore` so the standard blockstore tests can be reused against blobstore implementations.

## APIs, Flow, And State
`BlockStoreAdapter<B>` owns an `AsyncDropGuard<B>`. `exists`, `load`, `remove`, and `all_blocks` map `BlockId` to `BlobId { root: *id }`. `try_create` creates a blob, resizes it to the block payload length, writes from offset zero, and drops it. `store` loads or creates the blob, resizes if needed, writes the full data, and drops it. `num_blocks` counts test-only `all_blobs`, and `estimate_num_free_bytes` multiplies logical block size by the blobstore's estimated block count.

## Dependencies And Integration
Implements `BlockStoreReader`, `BlockStoreWriter`, `BlockStoreDeleter`, `AsyncDrop`, and marker `LLBlockStore`. It uses blob `read_all`, `resize`, `write`, and async drop to provide blockstore semantics.

## Risks And Test Signals
The adapter has zero overhead from the blockstore perspective even though the blobstore may have internal metadata, so size-related assertions are adapted rather than storage-physical. It unwraps async-drop errors in some cleanup paths, so failures there panic tests. The generic blockstore suite provides broad behavioral coverage through this shim.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/block_store_adapter.rs -->
