<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_node.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_node.rs

**Purpose**
`DataNode` is the enum wrapper that dispatches between inner and leaf node representations for block-backed blob trees.

**Important APIs, Types, And Functions**
The enum variants are `Inner(DataInnerNode<B>)` and `Leaf(DataLeafNode<B>)`. `parse` validates loaded block size and format version, then chooses leaf vs inner based on depth. Other APIs include `depth`, `block_id`, `raw_blockdata`, `_into_block`, `flush`, `convert_to_new_inner_node`, `overwrite_node_with`, `into_inner_node`, and `into_leaf_node`.

**Control Flow**
Parsing creates a binary-layout view, verifies the configured block size and supported format header, then delegates to `DataLeafNode::new` for depth 0 or `DataInnerNode::new` otherwise. `convert_to_new_inner_node` consumes an existing node’s block, zeroes the full payload, initializes it as a new inner node whose first child is the provided node, and returns a validated inner node. `overwrite_node_with` copies raw bytes from a source node into the destination block, preserving the destination block ID, then reparses the block.

**State And Persistence**
The enum owns the underlying block through the variant. Conversion and overwrite mutate block contents in memory; flush is required to push dirty data down to the blockstore when using cached/shared stores.

**Dependencies And Integration Points**
It depends on both node variants, `NodeLayout`, `binary_layout`, `BlockStore`, `BlockId`, `Data`, and `ZeroedData`. Higher tree and node-store code use it for generic node handling.

**Risks**
Wrong source or destination layouts trigger asserts. Overwrite can intentionally change a block from leaf to inner or inner to leaf, so callers must maintain tree invariants around references and depth.

**Test Signals**
Tests cover parse success/failure, invalid block sizes, wrong format, too-deep/too-many/too-few nodes, conversion zeroing, removal through node store, depth, overwrite combinations, and layout mismatch panics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_node.rs -->
