<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/interface.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/interface.rs

## Purpose
Defines the public high-level blob and blobstore traits for CryFS.

## APIs, Flow, And State
`Blob` exposes identity, byte length, resize, full and partial reads, fallible partial read, write, flush, node count, consuming remove, and `all_blocks`. `BlobStore` exposes create, ID-specific try-create/load/remove, node counts, capacity estimate, logical block size, cache flush by blob ID, and test/testutils cache clearing. `BLOBID_LEN` aliases `cryfs_blockstore::BLOCKID_LEN`.

## Dependencies And Integration
Uses `anyhow`, `async_trait`, `byte_unit`, `futures::BoxStream`, `cryfs_utils::data::Data`, and blockstore `BlockId`/`RemoveResult`. `BlobId` is a thin blob-level identity rooted in block IDs.

## Risks And Test Signals
Several comments mark abstraction leaks: `num_nodes` and `all_blocks` expose block-backed internals, and read-only methods require `&mut self`. These traits are the main contract consumed by on-block implementations, tracking wrappers, async shared wrappers, and blobstore tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/interface.rs -->
