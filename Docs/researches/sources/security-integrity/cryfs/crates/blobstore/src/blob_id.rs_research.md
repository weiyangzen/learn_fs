<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/blob_id.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/blob_id.rs

**Purpose**
This file defines `BlobId`, the blobstore-level identifier wrapper around a blockstore `BlockId`. In the block-backed implementation, a blob ID is the root data-tree block ID.

**Important APIs, Types, And Functions**
`BlobId` derives copy, ordering, hashing, and binary read/write traits. Constructors and conversions include `new_random`, `zero`, `to_root_block_id`, `from_root_block_id`, `from_slice`, `from_array`, `data`, `from_hex`, and `to_hex`. Display delegates to the root block ID; Debug formats as `BlobId(<hex>)`.

**Control Flow**
All conversion methods delegate validation and byte/hex parsing to `BlockId`. The block-backed store constructs blob IDs from root nodes and uses the `root` field internally.

**State And Persistence**
The only state is the embedded 16-byte block ID. Through `BinRead`/`BinWrite`, it can be serialized in binary formats alongside block IDs.

**Dependencies And Integration Points**
It depends on `cryfs_blockstore::{BlockId, BLOCKID_LEN}` and `binrw`. Public blobstore traits and implementations use `BlobId` for create/load/remove operations.

**Risks**
`root` remains `pub(super)` with a TODO to hide it behind `to_root_block_id`, so sibling modules can still couple to internal representation. Any future blob ID format change must preserve or migrate root-block semantics.

**Test Signals**
Unit tests cover Display and Debug formatting from a fixed hex ID; broader conversion and serialization behavior is not directly covered in this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/blob_id.rs -->
