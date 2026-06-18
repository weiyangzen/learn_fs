## sources/security-integrity/cryfs/crates/check/tests/node_missing.rs

Purpose: validates `NodeMissingError` reporting when data-tree nodes referenced by readable structures are removed from the nodestore.

Important APIs and functions: tests cover missing root nodes, inner nodes, leaf nodes, and multiple removed nodes. They use fixture removal methods (`remove_root_node_of_blob`, `remove_an_inner_node_of_a_large_blob`, `remove_a_leaf_node`, `remove_some_nodes_of_a_large_blob`) and common expectation helpers for orphaned nodes/blobs.

Control flow and state: each test creates a populated fixture, selects file/dir/symlink/root blobs, expands the root directory when necessary to ensure large enough depth, collects directory descendants before corruption, removes target nodes, derives expected missing and unreferenced errors, runs `cryfs_check`, and asserts unordered equality.

Dependencies and integration: depends on `BlobType` to add `BlobUnreadableError` expectations for directory blobs whose data cannot be decoded after node loss. It integrates checker traversal semantics with nodestore-level deletion.

Risks and test signals: the tests make a clear distinction between nodes directly referenced by still-reachable parents (`NodeMissing`) and children orphaned by removing an ancestor (`NodeUnreferenced`). A TODO notes missing coverage for `NodeMissing` with multiple references.
