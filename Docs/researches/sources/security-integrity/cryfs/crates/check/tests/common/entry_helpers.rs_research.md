## sources/security-integrity/cryfs/crates/check/tests/common/entry_helpers.rs

Purpose: shared fixture utilities for creating filesystem blobs, forcing multi-node data trees, selecting deterministic nodes, traversing descendants, and constructing expected checker errors.

Important APIs and types: `CreatedDirBlob`, `CreatedFileBlob`, and `CreatedSymlinkBlob` wrap `AsyncDropGuard<FsBlob<B>>` with path metadata and convert into `BlobReferenceWithId`. Creation helpers include `create_empty_dir`, `create_empty_file`, `create_symlink`, `create_large_file`, `create_large_symlink`, `create_large_dir`, and `create_large_dir_with_large_entries`. `SomeBlobs` captures a reusable graph of nested directories, large files, large symlinks, and empty blobs. Node search helpers include `find_leaf_node_*`, `find_inner_node_*`, and large/small blob shortcuts. Expectation helpers build `NodeUnreferencedError`s from live node ids.

Control flow and state: helpers mutate parent directory blobs by adding entries, write deterministic test data, recursively create deep/large structures, and explicitly async-drop guards to flush changes. Random node selection uses `SmallRng::seed_from_u64(0)` to keep tests reproducible.

Dependencies and integration: bridges `cryfs_blobstore`, `cryfs_blockstore`, `cryfs_fsblobstore`, `cryfs_check`, and `cryfs_utils`. It is the central integration layer between high-level test scenarios and low-level node/block operations.

Risks and test signals: assumptions about node depth/fanout are enforced with asserts that explain fixture-size adjustments. Recursive descendant streams can expose cycles or unreadable directories if corruption creates pathological references, so tests using them must account for traversal cutoff errors.
