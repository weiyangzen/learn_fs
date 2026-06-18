# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/store.rs

Purpose: defines `DataTreeStore<B>`, the high-level store for creating, loading, removing, flushing, and enumerating byte trees backed by `DataNodeStore`.

Important APIs and types: `DataTreeStore` wraps `AsyncDropGuard<AsyncDropArc<DataNodeStore<B>>>` so loaded trees share the node store with async-drop semantics. Public APIs include `new`, `load_tree`, `create_tree`, `try_create_tree`, `remove_tree_by_id`, `num_nodes`, `estimate_space_for_num_blocks_left`, `logical_block_size_bytes`, `load_block_depth`, `into_inner_node_store`, `load_all_nodes_in_subtree_of_id`, `flush_tree_if_cached`, and test-only `all_tree_roots`/cache clearing.

Control flow: construction delegates block-size validation to `DataNodeStore::new`. `create_tree` creates one empty leaf and wraps it as a `DataTree`; `try_create_tree` does the same at a caller-provided root ID and returns `None` on collision. `load_tree` loads a root node and wraps it if present. `remove_tree_by_id` loads a tree and calls `DataTree::remove` for recursive deletion. `flush_tree_if_cached` reloads the entire tree and flushes it because there is no dirty-node index yet.

State and persistence behavior: persistent tree state is the graph of node blocks rooted at a `BlockId`; the store itself holds only the shared node store. Removing a tree deletes the recursive subtree, not just the root. `all_tree_roots` reconstructs candidate roots by loading all nodes and subtracting every child ID, which is intentionally test-only and inefficient. Async drop delegates to the shared node store.

Dependencies and integration points: integrates lower-level `DataNodeStore`, `DataTree`, and traversal subtree streaming. It is the likely external API for blob/file data storage and is used extensively by `data_tree_store/testutils.rs` and `tree/tests.rs`.

Risks: `load_tree` trusts the caller-provided root ID; if it points to an interior node, the returned tree treats that subtree as an independent tree. `flush_tree_if_cached` is expensive and has a TODO noting lack of dirty tracking. `load_block_depth` is marked TODO Test. Shared `AsyncDropArc` requires careful ownership so active trees do not outlive required drops.

Test signals: embedded tests cover invalid/valid construction, tree loading, create and try-create behavior, ID collision, recursive removal including preserving other trees, node counts after add/remove, free-space estimation, and logical block size. `all_tree_roots` supports testing root discovery but is not a production path.
