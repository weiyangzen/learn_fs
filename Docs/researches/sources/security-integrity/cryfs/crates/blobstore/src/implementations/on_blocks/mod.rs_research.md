<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/mod.rs

## Purpose
Assembles and re-exports the blobstore implementation that stores blobs as block-backed data trees. It exposes the public on-blocks types and instantiates the generic blobstore test suite for several block sizes.

## APIs, Flow, And State
The module declares `data_node_store`, `data_tree_store`, `blob_on_blocks`, and `blobstore_on_blocks`, then re-exports `BlobOnBlocks`, `BlobStoreOnBlocks`, `DataNodeStore`, node types, `DataTree`, `DataTreeStore`, and `LoadNodeError`. Test fixtures create `BlobStoreOnBlocks<LockingBlockStore<InMemoryBlockStore>>` with block sizes ranging from the minimal node-header-plus-two-IDs size through 1 KiB, 32 KiB, and 4 MiB.

## Dependencies And Integration
This is the integration boundary between `cryfs_blobstore` and `cryfs_blockstore`: the blobstore is backed by a high-level `LockingBlockStore` over an `InMemoryBlockStore`. It uses `byte_unit::Byte`, async fixture construction, and `instantiate_tests_for_blobstore!`, which also tests the blobstore through the low-level blockstore adapter.

## Risks And Test Signals
The minimal block-size fixture protects node layout assumptions, while larger sizes exercise realistic capacities. The TODO notes that the generic blockstore tests need sufficiently large data cases to actually cover the tree structure; otherwise small tests can pass while multi-node behavior regresses.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/mod.rs -->
