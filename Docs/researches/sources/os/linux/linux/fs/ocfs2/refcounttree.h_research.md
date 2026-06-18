# File Research: sources/os/linux/linux/fs/ocfs2/refcounttree.h

`refcounttree.h` declares OCFS2’s refcount tree data structure and public APIs for shared extents, CoW, reflink, and refcounted xattr handling.

Main contents:
- Defines `struct ocfs2_refcount_tree`, which combines:
  - rbtree membership keyed by root block number.
  - root block number and generation.
  - kref lifetime management.
  - rw semaphore and OCFS2 lock resource for cluster-visible serialization.
  - metadata caching fields: spinlock, `ocfs2_caching_info`, I/O mutex, and superblock pointer.
  - `rf_removed` to mark stale trees removed from the global cache.
- Declares tree lifecycle and locking:
  - `ocfs2_purge_refcount_trees()`
  - `ocfs2_lock_refcount_tree()`
  - `ocfs2_unlock_refcount_tree()`
- Declares refcount update and CoW APIs:
  - `ocfs2_increase_refcount()`
  - `ocfs2_decrease_refcount()`
  - `ocfs2_prepare_refcount_change_for_del()`
  - `ocfs2_refcount_cow()`
  - `ocfs2_add_refcount_flag()`
  - `ocfs2_remove_refcount_tree()`
  - `ocfs2_try_remove_refcount_tree()`
- Defines `struct ocfs2_post_refcount`, a callback hook allowing callers to perform extra journaled work inside refcount transactions.
- Declares xattr-specific refcount helpers:
  - `ocfs2_refcounted_xattr_delete_need()`
  - `ocfs2_refcount_cow_xattr()`
- Declares cluster duplication and writeback helpers:
  - `ocfs2_duplicate_clusters_by_page()`
  - `ocfs2_duplicate_clusters_by_jbd()`
  - `ocfs2_cow_sync_writeback()`
- Declares reflink interfaces:
  - ioctl path creation through `ocfs2_reflink_ioctl()`.
  - range remap through `ocfs2_reflink_remap_blocks()`.
  - paired inode locking/unlocking.
  - destination size update.

Key invariants:
- The header exposes refcount operations to allocation, xattr, ioctl, and file remap code while keeping the record-splitting implementation private to `refcounttree.c`.
- Callers that need extra journaled side effects use `ocfs2_post_refcount` so those changes share the same transaction as refcount updates.
