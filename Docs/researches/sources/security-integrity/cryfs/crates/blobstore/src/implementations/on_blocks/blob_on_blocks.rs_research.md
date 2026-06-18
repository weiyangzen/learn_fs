<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blob_on_blocks.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blob_on_blocks.rs

**Purpose**
`BlobOnBlocks` adapts a `DataTree` into the public `Blob` trait, making a block-backed data tree look like a byte-addressable blob.

**Important APIs, Types, And Functions**
The struct stores `tree: AsyncDropGuard<DataTree<B>>`. `new` wraps a tree. `_tree` and `_tree_mut` expose references internally. `into_data_tree` is available for tests/testutils. The `Blob` implementation provides `id`, `num_bytes`, `resize`, `read_all`, `read`, `try_read`, `write`, `flush`, `num_nodes`, `remove`, and `all_blocks`.

**Control Flow**
Every blob operation delegates to the underlying `DataTree`. `id` returns a `BlobId` whose root is `tree.root_node_id()`. `remove` consumes the async-drop guard, extracts the tree without dropping it, and calls `DataTree::remove`. `AsyncDrop` delegates to the guarded tree.

**State And Persistence**
State is the guarded tree, which may include cached dirty nodes and references to the underlying blockstore. Persistence happens when the tree flushes or removes blocks through lower layers.

**Dependencies And Integration Points**
It depends on the public `Blob` trait, `BlobId`, `BlockStore`, `BlockId`, `AsyncDropGuard`, `Data`, and futures streams. `BlobStoreOnBlocks` creates and loads these objects.

**Risks**
The consume-without-drop path in `remove` relies on `DataTree::remove` handling cleanup completely. The trait requires `&mut self` for read-only operations, which simplifies cache mutation but constrains callers.

**Test Signals**
The broader blobstore tests exercise this adapter via public blob operations; `into_data_tree` supports lower-level test inspection.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blob_on_blocks.rs -->
