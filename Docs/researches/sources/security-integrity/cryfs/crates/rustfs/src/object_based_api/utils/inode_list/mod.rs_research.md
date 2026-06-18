# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/mod.rs

Purpose: tracks all inode numbers handed to the FUSE kernel and ties them to object nodes, parent relationships, lookup refcounts, and async-drop lifecycle.

Important APIs: constants `FUSE_ROOT_ID` and `DUMMY_INO`; `InodeList::new`, `insert_rootdir`, `get_node_and_parent_ino`, `get_node`, `add`, `add_or_increment_refcount`, `forget`, `make_into_orphan`, `move_inode`, test-only `clear_all_slow` and `fsync_all`; error enums.

Control flow and state: inner state holds a `ConcurrentStore<InodeNumber, Fs::Node>` and `HandleForest<InodeNumber, PathComponentBuf, InodeTreeNode<Fs>>` under a Tokio mutex. Root insertion establishes invariants. Lookup either increments an existing child refcount or inserts a loading child, waits outside the lock, then cleans up forest and parent refcount on load failure. Forget decrements refcount and removes zero-refcount leaf nodes, cascading to parents when child references were the last references. Removed handles are released only after async drops confirm store absence. Orphaning removes a parent child edge without dropping a loaded inode; moving updates parent edges and parent refcounts.

Dependencies and integration: central to `ObjectBasedFsAdapterLL` lookup, forget, create, unlink, rmdir, rename, getattr, and readdir parent references.

Risks and tests: invariants are extensive and many violations panic. Shutdown drops remaining inodes because the kernel may omit forgets. TODOs note deadlock/performance risks, cloned refs, and missing assertions. Test utilities can clear and fsync caches.
