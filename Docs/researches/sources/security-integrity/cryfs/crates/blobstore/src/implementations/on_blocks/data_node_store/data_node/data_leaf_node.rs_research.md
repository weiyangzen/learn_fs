<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_leaf_node.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_leaf_node.rs

**Purpose**
This file implements `DataLeafNode`, the serialized tree node that stores actual blob bytes in the block-backed blob data tree.

**Important APIs, Types, And Functions**
`DataLeafNode::new` validates format version, depth zero, exact block size, and stored byte count not exceeding layout capacity. Accessors and mutators include `block_id`, `raw_blockdata`, `into_block`, `flush`, `num_bytes`, `max_bytes_per_leaf`, `resize`, `data`, `data_mut`, and `upcast`. `serialize_leaf_node_optimized` writes the node header around a preallocated data region.

**Control Flow**
Loading reads the binary layout header and wraps the block only after validation. `resize` changes the logical size and zeroes bytes that become unused when shrinking, so shrinking then growing does not expose old data. `data` and `data_mut` return slices limited to the current logical size. Serialization grows the `Data` region backward to include the header, writes format/depth/size fields, and leaves the data region in place.

**State And Persistence**
The node owns a mutable block payload. In-memory mutations are not necessarily durable until `flush` is called through the blockstore stack.

**Dependencies And Integration Points**
It depends on `binary_layout`, `byte_unit`, `NodeLayout`, `BlockStore`, `BlockId`, and CryFS `Data`. `DataNodeStore` uses it for leaf creation, overwrite, and load.

**Risks**
Oversized writes and invalid serialization preconditions panic. `serialize_leaf_node_optimized` has a TODO to assert unused bytes are zeroed; callers currently ensure this by allocating/zeroing or by resize zeroing.

**Test Signals**
Tests cover valid/invalid loads, wrong format/depth/size, serialization fields, resize growth/shrink zeroing, mutable data access, block size behavior, byte count, into-block, and upcast behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_leaf_node.rs -->
