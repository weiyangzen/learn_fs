# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/handle_forest.rs

Purpose: generic forest of handle-addressed nodes with parent/child edge tracking and handle allocation.

Important APIs: `HandleForest::new`, `block_handle`, `get`, `get_mut`, `try_insert_root_with_specific_handle`, `get_child_of_mut`, async `try_insert`, `try_remove`, `make_node_into_orphan`, `move_node`, test-only `drain`, and error/result enums.

Control flow and state: combines `HandlePool` and `AsyncDropHashMap<Handle, Node<...>>`. Insert transactionally acquires a handle, inserts into the parent child map, constructs node value only on success, and undoes acquisition on duplicate edge. Remove refuses nodes with children, removes the child pointer from the parent if present, returns the node value and a delayed handle release. Move removes an edge from the old parent, reinserts into new parent, updates the child's parent pointer, and restores the old edge if the new parent is missing.

Dependencies and integration: used by `InodeList` to model kernel-visible inode parentage. Depends on `Node`, `HandlePool`, async drop containers, and `DelayedHandleRelease`.

Risks and tests: many invariants are enforced by panics. Overwriting an existing child during move orphans that child. Comments document cases where parent pointers may remain on orphaned nodes.
