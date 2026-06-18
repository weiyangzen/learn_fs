<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/layout.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/layout.rs

**Purpose**
This file defines the on-disk/in-block binary layout for data-tree nodes and helper calculations for leaf and inner-node capacity.

**Important APIs, Types, And Functions**
`FORMAT_VERSION_HEADER` is currently 0. The `binary_layout!` macro defines `node` fields: `format_version_header: u16`, `unused: u8`, `depth: u8`, `size: u32`, and variable `data: [u8]`. `NodeLayout` stores `block_size: Byte` and provides `header_len` in tests, `max_bytes_per_leaf`, `max_children_per_inner_node`, and `num_leaves_per_full_subtree`.

**Control Flow**
Capacity calculations subtract the header offset from usable block size. Inner-node fanout divides that data capacity by `BLOCKID_LEN`. Full-subtree leaf capacity raises fanout to the requested depth with checked overflow and returns `NonZeroU64`.

**State And Persistence**
The layout defines persisted bytes in every data node. The unused byte is reserved for alignment/future use. Format version guards compatibility.

**Dependencies And Integration Points**
It depends on `binary_layout`, `byte_unit`, `anyhow`, and `cryfs_blockstore::BLOCKID_LEN`. Inner and leaf node code use the generated view accessors for serialization and validation.

**Risks**
Several conversions use casts/TODOs rather than fully checked conversions. Layout changes require migration logic because old nodes validate against `FORMAT_VERSION_HEADER`.

**Test Signals**
Unit tests cover header offset, maximum leaf bytes, maximum children, and subtree leaf-count exponentiation for representative depths.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/layout.rs -->
