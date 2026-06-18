<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blobstore_on_blocks.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blobstore_on_blocks.rs

**Purpose**
`BlobStoreOnBlocks` adapts a `DataTreeStore` over a `BlockStore` into the public `BlobStore` trait.

**Important APIs, Types, And Functions**
The struct owns `tree_store: AsyncDropGuard<DataTreeStore<B>>`. `new` constructs a `DataTreeStore` from an async-drop blockstore and physical block size. `load_block_depth` exposes tree-store depth loading. `into_inner_tree_store` supports consuming the wrapper. The `BlobStore` implementation maps create/load/try-create/remove/flush/all-blobs operations to tree-store operations and wraps trees as `BlobOnBlocks`.

**Control Flow**
`create` calls `create_tree`; `try_create` and `load` pass root `BlockId`s from `BlobId`; `remove_by_id` calls `remove_tree_by_id`; cache and size methods delegate unchanged. `AsyncDrop` drops the tree store.

**State And Persistence**
State is the guarded tree store and its underlying blockstore/cache. Persistence semantics are delegated to tree/node/blockstore flush and remove behavior.

**Dependencies And Integration Points**
It bridges the public `BlobStore` trait, `BlobId`, `RemoveResult`, `DataTreeStore`, `BlockStore`, and `AsyncDropGuard`. It is the main concrete blobstore exported by the crate.

**Risks**
It accesses `BlobId.root` directly, so representation changes in `BlobId` require coordinated updates. Debug output is intentionally generic and does not expose the inner store.

**Test Signals**
Workspace blobstore tests and blockstore-adapter tests validate this implementation through trait-level behavior and feature-gated helpers.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blobstore_on_blocks.rs -->
