# File Research: sources/os/linux/linux-stable/fs/ocfs2/refcounttree.h

Purpose: declares OCFS2 refcount tree state and public APIs for COW, reflink, refcount adjustment, xattr refcounting, and reflink inode locking.

Read coverage: complete file read, 127 lines.

Key contents:
- Defines `struct ocfs2_refcount_tree`, the in-memory cached refcount-tree object keyed by root block number.
- The structure embeds rb-tree linkage, root block number, generation, kref, local rwsem, cluster lock resource, removal flag, metadata cache state, cache spinlock, I/O mutex, and superblock pointer.
- Declares tree lock/unlock/purge APIs: `ocfs2_lock_refcount_tree()`, `ocfs2_unlock_refcount_tree()`, `ocfs2_purge_refcount_trees()`.
- Declares refcount mutation APIs: `ocfs2_increase_refcount()`, `ocfs2_decrease_refcount()`, `ocfs2_prepare_refcount_change_for_del()`, `ocfs2_add_refcount_flag()`, `ocfs2_remove_refcount_tree()`, `ocfs2_try_remove_refcount_tree()`.
- Declares COW and duplication APIs for file data and xattr data.
- Defines `struct ocfs2_post_refcount`, allowing callers to run extra journaled work inside a refcount transaction.
- Declares reflink ioctl, block remap, destination-size update, and double-inode lock helpers.

Dependencies and risks:
- The header exposes transaction-coupled interfaces that require callers to pass correct handles, alloc contexts, cached deallocation contexts, and already-locked metadata where documented.
- `ocfs2_post_refcount` makes transaction credit accounting caller-sensitive; incorrect credit values can break COW/xattr updates.
