<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_inner_node.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_inner_node.rs

**Purpose**
This file implements `DataInnerNode`, the serialized tree node that stores child block IDs for non-leaf levels in the block-backed blob data tree.

**Important APIs, Types, And Functions**
`MAX_DEPTH` is 10. `DataInnerNode::new` validates format version, nonzero depth, exact block size, maximum depth, and child count range. Accessors include `depth`, `block_id`, `raw_blockdata`, `into_block`, `flush`, `num_children`, `children`, and `upcast`. Mutation APIs include test-only `update_child`, `add_child`, and `shrink_num_children`. Serialization helpers are `serialize_inner_node`, `initialize_inner_node`, and `_serialize_children`.

**Control Flow**
Loading constructs a binary-layout view over block data and enforces invariants before wrapping the block. Child iteration slices the data region into `BLOCKID_LEN` chunks and converts each used chunk to a `BlockId`. Adding a child checks the child depth is exactly one lower, writes the new child ID into the next slot, and increments `size`. Shrinking validates the new count is not larger, zeroes freed child slots, and writes the smaller size.

**State And Persistence**
State is the mutable block payload owned by the node. Mutations update the in-memory block; persistence requires `flush` through the blockstore or higher-level tree flushing.

**Dependencies And Integration Points**
It depends on `binary_layout`, `NodeLayout`, `BlockId`, `BlockStore`, `Data`, and `ZeroedData`. `DataNode` dispatches to it for parse/upcast behavior; `DataNodeStore` creates and flushes it.

**Risks**
Some invariant violations are `assert!` panics rather than recoverable errors, especially wrong node kind or invalid serialization parameters. Callers must avoid adding children to full nodes and must flush dirty changes for durable persistence.

**Test Signals**
Extensive tests cover loading failures, serialization, child addition at multiple depths, full-node failure, shrinking and zeroing, child iteration, depth, raw block conversion, and upcast behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_inner_node.rs -->
