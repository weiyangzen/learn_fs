## sources/security-integrity/cryfs/crates/check/tests/node_unreferenced.rs

Purpose: validates reporting of nodes that exist in the nodestore but are not reachable from any blob rooted at the filesystem root.

Important APIs and functions: `leaf_node_unreferenced` creates an orphan leaf with empty data. `single_inner_node_unreferenced` creates an orphan inner node that references two nonexistent child ids. `inner_node_with_subtree_unreferenced` creates a complete orphan subtree of leaves and inner nodes.

Control flow and state: tests use `update_nodestore` to create raw data nodes outside any blob. Expected errors include `NodeUnreferencedError` for the orphan root node. The single-inner case also expects `NodeMissingError` for its fake child pointers because an unreferenced inner node is still inspected and its children are missing. The complete-subtree case expects only the top unreferenced root because descendants are reachable from that orphan subtree.

Dependencies and integration: depends on `BlockId`, `Data`, `DataFixture`, `NodeInfoAsSeenByLookingAtNode`, `NodeAndBlobReference`, and `MaybeBlobReferenceWithId::UnreachableFromFilesystemRoot`.

Risks and test signals: this file probes checker behavior beyond filesystem-root traversal by requiring inventory scanning of all stored nodes. It clarifies that unreachable subtrees are summarized at their orphan root when internally consistent.
