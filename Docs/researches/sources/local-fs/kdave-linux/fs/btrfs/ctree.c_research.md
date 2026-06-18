# File Research: sources/local-fs/kdave-linux/fs/btrfs/ctree.c

Core Btrfs copy-on-write B-tree implementation, covering path allocation, key search, node/leaf balancing, block COW, insertion, deletion, item mutation, and tree traversal.

Key responsibilities:
- Allocates, releases, and frees `btrfs_path` objects through a slab cache, dropping locks and extent-buffer references consistently.
- Provides safe root-node reference acquisition with RCU and dirty-root tracking for cow-only roots.
- Copies roots for snapshots/relocation, decides when blocks can be shared, updates backrefs for COW, and performs forced or conditional block COW.
- Implements key comparison and binary search across leaf and node extent buffers, including fast little-endian key comparison.
- Reads child nodes with parent checks for level, transid, owner root, and first key.
- Implements `btrfs_search_slot()` and `btrfs_search_old_slot()`, including lock-level escalation, nowait reads, commit-root searches, tree-mod-log rewind, path restarts, readahead, and COW during modifying searches.
- Balances internal nodes during insertion and deletion, including promoting a single child to root, pushing pointers left/right, inserting new root levels, and splitting full nodes.
- Balances leaves by pushing items left/right, splitting leaves, avoiding double splits when possible, and maintaining parent low keys.
- Provides item mutation helpers for safe key update, item split, duplicate, truncate, extend, single/batch insertion, and deletion.
- Deletes empty leaves and tree pointers, frees tree blocks, and updates root used-byte accounting.
- Provides forward, backward, old-version, and next-item traversal helpers used by defrag, send, logging, and metadata walkers.
- Initializes and destroys the path slab cache.

Dependencies:
- Uses Btrfs transaction, locking, disk I/O, extent tree, qgroup, relocation, tree-mod-log, tree-checker, file-item, print-tree, and accessor infrastructure.
- Depends on extent buffers, Btrfs tree block allocation/freeing, delayed refs/backrefs, RCU root pointer replacement, lockdep nesting classes, and error injection hooks.

Notable risks:
- Search paths deliberately release and reacquire locks, returning `-EAGAIN` for restarts; callers must respect path invalidation rules.
- COW/backref logic distinguishes shareable roots, relocation roots, full backrefs, commit roots, and last-ref cases; mistakes can corrupt metadata ownership.
- Many helpers use `BUG_ON`, `WARN_ON`, and transaction aborts when invariants fail, so malformed metadata or incorrect caller state can take the filesystem read-only or crash debug paths.
- Leaf item layout is manually maintained with offset/size arrays growing opposite data storage; off-by-one or size accounting errors directly corrupt tree blocks.
- Parent low-key updates are required when slot 0 changes; callers using `btrfs_set_item_key_safe()` remain responsible for preserving key order.
- Old-root and commit-root searches rely on tree-mod-log and commit semaphore rules, with special cloning for callers that cannot block transaction commits.
