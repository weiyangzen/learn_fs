<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/mod.rs

**Purpose**
This module groups the concrete data-node variants and exposes their public wrapper types to the parent data-node store.

**Important APIs, Types, And Functions**
It declares `mod data_inner_node`, `mod data_leaf_node`, and `mod data_node`, then re-exports `DataInnerNode`, `DataLeafNode`, and `DataNode`.

**Control Flow**
Parent modules import node types through this module rather than addressing each file directly.

**State And Persistence**
The module has no state. Persistence behavior lives in the re-exported node implementations.

**Dependencies And Integration Points**
It is the integration point between `data_node_store` and the separate inner/leaf/enum implementation files.

**Risks**
No direct logic risk. Re-export shape determines which node internals become visible to sibling modules and crate users through higher-level re-exports.

**Test Signals**
Compilation of `data_node_store` and its tests validates this module wiring.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/mod.rs -->
