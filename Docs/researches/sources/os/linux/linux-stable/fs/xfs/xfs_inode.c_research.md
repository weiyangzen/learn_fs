# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode.c

## Purpose

Implements core XFS inode operations: inode locking, namespace mutations, inode creation, truncation and inactivation, unlinked-list recovery, inode freeing, inode flushing, layout breaking, and helper utilities.

## Main Responsibilities

- Provides multi-lock inode locking primitives over VFS `i_rwsem`, mapping `invalidate_lock`, and XFS `i_lock`.
- Implements directory namespace operations:
  - lookup
  - create
  - tmpfile create
  - hardlink
  - remove
  - rename, exchange, and whiteout rename
- Initializes newly allocated inodes and dquot attachments.
- Truncates data/attr fork extents and cancels COW reservations.
- Runs inactive cleanup for unreferenced inodes.
- Frees unlinked inodes and handles inode-cluster stale marking.
- Waits for pinned inodes and forces log commits for inode fsync semantics.
- Flushes dirty inode state to inode cluster buffers and coordinates clustered inode writeback.
- Reloads incomplete incore unlinked-list state.
- Breaks leases and DAX layouts before extent-remapping operations.

## Locking Model

The file defines and enforces the XFS inode lock hierarchy:

- IOLOCK: VFS inode `i_rwsem`
- MMAPLOCK: mapping `invalidate_lock`
- ILOCK: XFS inode `i_lock`

`xfs_ilock`, `xfs_ilock_nowait`, `xfs_iunlock`, `xfs_ilock_demote`, and `xfs_assert_ilocked` operate on combinations of these locks. Multi-inode helpers sort or order locks by inode number and use lockdep subclasses:

- `xfs_lock_inodes`
- `xfs_lock_two_inodes`
- `xfs_ilock2_io_mmap`
- `xfs_iunlock2_io_mmap`
- `xfs_iunlock2_remapping`

## Namespace Operation Flow

- `xfs_lookup`
  - Looks up a directory name, igets the target inode, and rejects regular directory entries pointing to metadata files.
- `xfs_create`
  - Allocates dquots, reserves a transaction, allocates an inode, joins parent/child inodes, creates the directory entry and parent pointer data, attaches quotas, commits, and returns the locked-created inode after setup.
- `xfs_create_tmpfile`
  - Allocates an inode as an unlinked tmpfile and commits it on the unlinked list.
- `xfs_link`
  - Attaches dquots, checks project inheritance constraints, adds the directory entry, and commits the link transaction.
- `xfs_remove`
  - Removes a child directory entry and updates link/unlinked state through directory helper code while respecting AGI-before-AGF lock ordering.
- `xfs_rename`
  - Handles normal rename, exchange, and whiteout. It sorts all participating inodes, allocates parent-pointer contexts, optionally allocates a tmpfile whiteout inode, reserves quota/blocks, locks AGIs before directory block changes when needed, and delegates directory mutation to `xfs_dir_rename_children`.

## Inactivation and Freeing

- `xfs_inode_needs_inactive` decides whether inactive cleanup must run before reclaim.
- `xfs_inactive` cancels COW reservations, frees EOF blocks for linked files, truncates unlinked regular files/directories/symlinks, removes attributes, and frees the inode.
- `xfs_inactive_dir` marks incore directory buffers stale before a recovered temporary directory is discarded.
- `xfs_inactive_truncate` logs zero size before freeing extents to avoid stale data exposure after crash.
- `xfs_inactive_ifree` removes the inode from unlinked lists and returns it to free inode btrees.
- `xfs_ifree` uninitializes the inode, clears owner-change replay bits, and frees the backing inode cluster when the chunk becomes empty.
- `xfs_ifree_cluster` locks inode cluster buffers, marks all incore inodes in the cluster stale, and invalidates/stales the buffer transactionally.

## Unlinked List Recovery

- `xfs_iunlink_lookup` searches the per-AG inode cache while the AGI stabilizes unlinked-list existence.
- `xfs_iunlink_reload_next` reloads missing unlinked inodes into cache, validates zero nlink, and reconstructs `i_prev_unlinked`.
- `xfs_inode_reload_unlinked_bucket` walks an AGI unlinked bucket and reloads missing incore list links.
- `xfs_inode_reload_unlinked` provides the transaction wrapper for one inode.

## Inode Flush Flow

- `xfs_iflush` validates incore inode/fork state, updates flush iteration for old dinodes, verifies local forks, copies dirty core/forks to the ondisk dinode, computes CRC, and moves `ili_fields` to `ili_last_fields`.
- `xfs_iflush_cluster` scans all inode log items attached to a cluster buffer, nonblocking-locks eligible inodes, aborts on shutdown, and queues a delayed-write buffer when at least one inode flushes.
- `xfs_iunpin_wait` forces the log for the inode commit sequence and waits for the pin count to reach zero.
- `xfs_log_force_inode` synchronously forces the log through the last commit sequence that touched the inode.

## Important Invariants

- Directory tree lookups must not expose metadata-directory inodes as normal files.
- Project-inheritance directories reject links/renames that would bypass tree quota, except for legacy project-less special files.
- Truncation callers must hold the inode lock exclusively, must use a permanent log reservation, and may receive a rolled transaction.
- Inactive cleanup skips internal metadata inodes because they require explicit resource cleanup elsewhere.
- Inode freeing must mark all cached inodes in a freed cluster stale; missing one can leave dirty stale inodes attached to invalid buffers.
- Flush clears dirty fields only after copying them to the buffer and relies on `ili_last_fields` until buffer I/O completion makes them durable.
- Layout breaking distinguishes write breaks from unmap breaks; DAX unmap breaks must also wait for busy DAX pages.

## Dependencies

This file integrates with directory code, parent pointers, attributes, symlinks, inode allocation, bmap and bmap btrees, reflink/COW, quotas, filestreams, log transactions, AIL, buffer items, health state, pNFS, DAX, and VFS lease/layout APIs.

## Research Notes

`xfs_inode.c` is the core behavioral hub for XFS inode operations. The main complexity is not the individual namespace operations but their ordering constraints: inode locks, AGI/AGF ordering, transaction rolling, dquot accounting, unlinked-list recovery, stale cluster invalidation, and log-item flush coordination all have to line up.
