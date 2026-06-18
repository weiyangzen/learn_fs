# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/inode_tree_node.rs

Purpose: value stored in the inode handle forest, combining kernel lookup reference count with a shared loading/loaded inode guard.

Important APIs: `InodeTreeNode::new`, `increment_refcount`, `decrease_refcount`, `inode_future`, `RefcountInfo`, and `AsyncDrop`.

Control flow and state: `kernel_refcount` starts at 1. Decrease asserts no underflow and reports whether it reached zero. The inode payload is an `AsyncDropShared` future resolving to a `LoadedEntryGuard`; this allows multiple lookup waiters to share a pending load.

Dependencies and integration: used by `InodeList` to enforce FUSE lookup/forget semantics and keep concurrent store entries alive.

Risks and tests: refcount overflow and underflow panic. The nested async-drop/future type is complex and marked with TODOs suggesting improvements to `ConcurrentStore`.
