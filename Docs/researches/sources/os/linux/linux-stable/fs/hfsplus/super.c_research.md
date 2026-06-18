# File Research: sources/os/linux/linux-stable/fs/hfsplus/super.c

## Role

Filesystem registration, mount/fill-super logic, superblock operations, metadata inode loading/writing, volume header commit, sync/remount behavior, and module init/exit for the Linux HFS+ driver.

## Metadata Inode Loading and Writing

- `hfsplus_system_read_inode()` initializes special system inodes from volume-header fork records:
  - extents overflow file
  - catalog file
  - allocation file
  - startup file
  - attributes file
  - B-tree system files get `hfsplus_btree_aops`; allocation gets `hfsplus_aops`.
  - Assigns dummy `S_IFREG` mode so VFS open checks see a valid file type.
- `hfsplus_iget()`
  - Uses `iget_locked()`.
  - Initializes all HFS+ private inode fields on new inodes.
  - Loads user/root catalog inodes through catalog lookup/read.
  - Loads system inodes through `hfsplus_system_read_inode()`.
  - Calls `iget_failed()` on errors.
- `hfsplus_system_write_inode()`
  - Maps system inode CNIDs back to volume-header fork fields.
  - If total size changed, sets backup-header write and marks MDB dirty.
  - Writes fork data and, for B-tree inodes, writes the B-tree under nested tree lock.
- `hfsplus_write_inode()`
  - Flushes dirty extent state first.
  - Dispatches user/root inodes to catalog writeback and system inodes to volume-header fork writeback.
- `hfsplus_evict_inode()`
  - Truncates final pages, clears inode, and handles resource-fork backpointer/iput cleanup.

## Volume Header Commit and Sync

- `hfsplus_prepare_volume_header_for_commit()`
  - Sets Linux HFS+ mount version.
  - Updates modify date.
  - Increments write count.
  - Clears clean-unmounted bit and sets inconsistent bit before write activity.
- `hfsplus_commit_superblock()`
  - Under `vh_mutex` and `alloc_mutex`, writes mutable counters into the primary volume header.
  - Copies primary header to backup header if `HFSPLUS_SB_WRITEBACKUP` was set.
  - Writes primary volume header sector and optionally backup volume header sector through `hfsplus_submit_bio()`.
- `hfsplus_sync_fs()`
  - For wait syncs, explicitly writes catalog, extents, optional attributes, and allocation file mappings.
  - Commits the superblock.
  - Issues block-device flush unless `HFSPLUS_SB_NOBARRIER` is set.
- `hfsplus_mark_mdb_dirty()`
  - Skips read-only mounts.
  - Queues delayed sync work once, using `dirty_writeback_interval * 10`.
- `delayed_sync_fs()`
  - Clears queued state and runs `hfsplus_sync_fs()`.

## Unmount, Statfs, and Reconfigure

- `hfsplus_put_super()`
  - Cancels delayed sync work.
  - On writable mounts, sets modify date, marks clean unmounted, clears inconsistent, and syncs.
  - Drops allocation and hidden directory inodes, closes B-trees, frees volume header buffers.
- `hfsplus_statfs()` fills HFS+ statfs data from allocation counters and block geometry.
- `hfsplus_reconfigure()`
  - Syncs before changing read-only state.
  - Refuses read-write remount if not cleanly unmounted, soft-locked, or journaled unless `force` permits the latter checks according to mount logic.

## Mount Path

`hfsplus_fill_super()` performs the full mount:

1. Initializes locks and delayed work.
2. Loads requested/default NLS; temporarily switches to UTF-8 to find/create the hidden directory.
3. Reads wrapper/volume header with `hfsplus_read_wrapper()`.
4. Validates HFS+ version and copies volume header counters/geometric fields.
5. Checks filesystem size against sector and page-index limits.
6. Sets superblock operations and maximum file size.
7. Applies safety read-only policy for unclean, soft-locked, and journaled volumes unless force permits.
8. Opens extents and catalog B-trees.
9. Opens attributes B-tree if the attributes fork has blocks and sets xattr handlers.
10. Loads allocation file inode.
11. Loads root inode and builds root dentry.
12. Looks up the hidden directory under root.
13. On writable mounts, prepares/commits volume header and creates the hidden directory if absent, including security xattr initialization.
14. Restores the originally requested NLS table.

Error paths unwind hidden dir/root/allocation inode/B-trees/header buffers/NLS state.

## Filesystem Registration and Cache Lifecycle

- Defines `hfsplus_sops`.
- Allocates HFS+ inode cache with `kmem_cache_create()`.
- Initializes attributes tree cache.
- Registers `file_system_type` named `"hfsplus"` with block-device requirement and fs-context operations.
- `hfsplus_kill_super()` calls `kill_block_super()` then defers private superblock free through RCU.
- Exit unregisters filesystem, runs `rcu_barrier()`, destroys attribute cache, and destroys inode cache.

## Dependencies

Uses VFS block filesystem mount helpers, NLS, slab caches, delayed work, B-tree/catalog/allocation/xattr subsystems, wrapper block I/O, and HFS+ volume header structures.

## Research Notes

This file defines the driver’s safety posture: unclean, soft-locked, and journaled volumes are kept read-only unless permitted by `force` where applicable. It also explains why metadata inodes are explicitly written during sync: flusher writeback alone can redirty metadata and miss the latest state. The hidden directory is a Linux-driver implementation detail used for special HFS+ bookkeeping, and mount temporarily forces UTF-8 to find it consistently.
