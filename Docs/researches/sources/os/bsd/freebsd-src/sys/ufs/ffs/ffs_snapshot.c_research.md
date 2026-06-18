# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_snapshot.c

## Role

Implements FreeBSD FFS snapshot support: snapshot file creation, copy-on-write protection, snapshot mount/unmount reattachment, snapshot deletion cleanup, and deferred inactive processing around suspended filesystems.

When `NO_FFS_SNAPSHOT` is defined, this file provides stub entry points returning `EINVAL` or doing nothing. Otherwise it provides the active snapshot subsystem.

## Main Responsibilities

- Creates snapshot files through `ffs_snapshot()`.
- Preallocates snapshot file direct/indirect blocks and metadata copies.
- Suspends filesystem writes while building a consistent snapshot image.
- Copies cylinder group maps, superblock, summary information, and snapshot block lists into the snapshot file.
- Expunges unlinked active files and soft-updates journal state from the snapshot view.
- Maintains per-device `struct snapdata` with a shared snapshot lock, active snapshot list, and preallocated block hint list.
- Handles copy-on-write when filesystem/device buffers are about to be written.
- Handles block-free notifications so snapshots can claim or copy blocks before they disappear.
- Reattaches persisted snapshots at mount time and detaches them at unmount time.
- Removes snapshot-specific block markers before a snapshot file is deleted.
- Processes deletes and lazy access-time updates deferred while writes were suspended.

## Important Data Structures

- `struct snapdata`: per-device snapshot state, stored at `devvp->v_rdev->si_snapdata`.
- `sn_head`: active snapshot inode tail queue, oldest to newest.
- `sn_lock`: shared lock used as the vnode lock for snapshot vnodes.
- `sn_blklist`: sorted list of logical blocks preallocated or otherwise safe from ordinary COW checks.
- `fs->fs_snapinum[]`: persistent superblock snapshot inode list.
- `ip->i_nextsnap`: inode linkage in the active snapshot queue.
- `ip->i_snapblklist`: temporary pointer while building the final snapshot block list.
- Magic block pointer values:
  - `BLK_NOCOPY`: snapshot does not need a copy of this logical block.
  - `BLK_SNAP`: block is owned/claimed by snapshot semantics rather than ordinary file mapping.
  - `0`: snapshot still needs the original block if it changes.

## Snapshot Creation Flow

`ffs_snapshot()` performs a multi-phase creation:

1. Rejects gjournal mounts because snapshots are unsupported with gjournal.
2. Finds a free `fs_snapinum[]` slot.
3. Creates the target regular file with `VOP_CREATE()` on the same mount.
4. Marks the vnode `VV_SYSTEM`, initializes a VM object, and makes it an `SF_SNAPSHOT` inode.
5. Sets snapshot size to filesystem size plus one block for the snapshot block list.
6. Preallocates indirect blocks, superblock copy space, summary info blocks, and cylinder group blocks.
7. Copies cylinder group maps before suspension and tracks changed cylinder groups through `fs->fs_active`.
8. Syncs the snapshot vnode, unlocks it, and suspends filesystem writes with `vfs_write_suspend()`.
9. Re-copies cylinder groups changed during the first pass.
10. Copies the in-memory superblock and summary data to temporary memory.
11. Temporarily clears `MNTK_SUSPENDED` to inspect active vnodes.
12. Expunges unlinked active files and the SUJ journal from the snapshot image.
13. Preallocates all direct snapshot blocks to avoid later inode writes for COW commits.
14. Acquires/creates `snapdata`, switches the snapshot vnode to the shared `snaplk`, and links the inode into `sn_head`.
15. Resumes writes with `vfs_write_resume()`.
16. Expunges older snapshots from the new snapshot’s view and computes the final block list.
17. Writes the snapshot block list, summary info, and snapshot superblock into the snapshot file.

This is a good example of a filesystem snapshot built using an ordinary file plus special block-pointer semantics rather than a separate volume object.

## Cylinder Group and Metadata Accounting

`cgaccount()` copies a cylinder group block into the snapshot and marks free blocks as `BLK_NOCOPY` in the snapshot inode mapping. On a second pass it undoes stale `BLK_NOCOPY` marks for blocks that became allocated between the first copy and write suspension. It also updates cylinder group check hashes when enabled.

The UFS1 and UFS2 accounting code is duplicated by block pointer width:

- `expunge_ufs1()` / `expunge_ufs2()` clear an inode’s image in the snapshot and walk all direct/indirect blocks.
- `indiracct_ufs1()` / `indiracct_ufs2()` recursively traverse indirect block trees.
- `fullacct_*()` combines snapshot pointer marking with allocation bitmap updates.
- `snapacct_*()` marks blocks as `BLK_SNAP` or `BLK_NOCOPY` in the snapshot inode.
- `mapacct_*()` frees corresponding blocks from the copied allocation maps and optionally records logical block numbers in the snapshot block list.

## Copy-on-Write and Block-Free Handling

`ffs_copyonwrite()` is called from the FFS device strategy path before writes hit the underlying provider:

- Ignores writes to snapshot files themselves.
- Rejects recursive COW with `TDP_COWINPROGRESS`.
- Uses `sn_blklist` as a fast preallocated-block exclusion list.
- Locks the shared snapshot lock and checks each active snapshot inode.
- Allocates a snapshot block where needed, reads the old device block, and writes it into the snapshot.
- Writes synchronously for metadata, directories, or all data when `dopersistence` is enabled; otherwise it may use async writes.
- Temporarily backs the original buffer out of running-buffer accounting while waiting on snapshot locks.

`ffs_snapblkfree()` handles block deletion before free proceeds:

- If a full block is being freed and a snapshot needs it, the snapshot can claim the original block directly.
- If a fragment is being freed, snapshots copy the whole block because snapshots claim full blocks only.
- If a previous snapshot has already claimed the block, later snapshots can mark it `BLK_NOCOPY`.
- On allocation/copy failure, it returns non-zero to prevent freeing, preserving snapshot consistency at the cost of leaked space.

## Snapshot Lifecycle

- `ffs_snapshot_mount()` reads `fs_snapinum[]`, validates persisted snapshot files, switches their vnode locks to `sn_lock`, links them to `sn_head`, reads the newest snapshot block list, and enables `VV_COPYONWRITE` on the device vnode.
- `ffs_snapshot_unmount()` removes snapshot inodes from `sn_head`, restores vnode locks, drops references, and frees/recycles `snapdata` when possible.
- `ffs_snapgone()` handles last-name removal by dropping the extra snapshot vnode reference and deleting the inode number from `fs_snapinum[]`.
- `ffs_snapremove()` unlinks an active snapshot from the in-core list, clears `BLK_NOCOPY` / `BLK_SNAP` markers, pushes claimed blocks to other snapshots if needed, clears `SF_SNAPSHOT`, and re-enables quota charging.

## Locking and Concurrency

Snapshot locking is unusual and central to the file:

- All snapshots on a device share one `sn_lock`.
- Snapshot vnodes mutate `v_vnlock` from their private lock to `sn_lock`.
- `revert_snaplock()` safely restores a vnode’s private lock while preserving recursion counts.
- `ffs_snapdata_acquire()` publishes new `snapdata` with `sn_lock` already held to avoid races.
- `try_free_snapdata()` drains and recycles `snapdata`, but `snapdata` objects are kept on a free list rather than destroyed because threads may have slept on the lock.
- Device vnode interlock protects `si_snapdata`, `VV_COPYONWRITE`, and snapshot-list transitions.
- Several paths set `TDP_COWINPROGRESS` to prevent recursive snapshot allocation/COW loops.

## Buffer Flushing

`ffs_bdflush()` customizes dirty-buffer flushing when snapshots exist. It avoids flushing the triggering snapshot block in ways that would worsen snapshot lock contention, and it preferentially selects suitable dirty buffers. `ffs_bp_snapblk()` checks whether a buffer maps a block in the snapshot block list.

## Deferred Inactive Processing

`process_deferred_inactive()` is compiled regardless of snapshot support. It runs after suspended writes resume and:

- Converts `IN_LAZYACCESS` to `IN_MODIFIED`.
- Calls `vinactive()` for vnodes that owed inactive processing while the filesystem was suspended.
- Restarts vnode iteration when vnode locking races require it.

## Research Relevance

This file is highly relevant to filesystem research because it shows a mature in-kernel snapshot design layered onto FFS allocation metadata. It demonstrates write suspension, persistent snapshot discovery, block-level COW, interaction with soft updates, special vnode lock mutation, and correctness tradeoffs between metadata persistence and data persistence.
