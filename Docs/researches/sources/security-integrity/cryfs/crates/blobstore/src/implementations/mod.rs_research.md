<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/mod.rs

**Purpose**
This module collects and re-exports concrete blobstore implementations.

**Important APIs, Types, And Functions**
It declares `mod on_blocks;` and re-exports `BlobOnBlocks`, `BlobStoreOnBlocks`, `DataInnerNode`, `DataLeafNode`, `DataNode`, `DataNodeStore`, `DataTree`, `DataTreeStore`, and `LoadNodeError`. It also declares `mod shared;`. Under tests or the `testutils` feature, it exposes the `tracking` implementation and re-exports `BlobStoreActionCounts` and `TrackingBlobStore`.

**Control Flow**
Consumers import concrete types from `crate::implementations` or from the crate root, which itself re-exports these symbols.

**State And Persistence**
The module has no state. It shapes the public module boundary for implementation types.

**Dependencies And Integration Points**
It integrates the on-blocks storage stack with optional test tracking utilities.

**Risks**
Re-exporting internal data-node/tree types exposes implementation details, making later refactors more compatibility-sensitive. The conditional tracking exports must match feature gates in `Cargo.toml`.

**Test Signals**
Compilation under test, default, no-default, and all-features modes validates the feature gating and public export graph.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/mod.rs -->
