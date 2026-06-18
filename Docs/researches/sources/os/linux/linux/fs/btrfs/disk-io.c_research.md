# File Research: sources/os/linux/linux/fs/btrfs/disk-io.c

## Purpose

`disk-io.c` is a central Btrfs mount, metadata I/O, root-management, superblock, transaction-cleanup, and filesystem shutdown implementation. It ties together superblock validation, tree block reads/writes, root loading, workqueue setup, log replay, writable mount preparation, superblock commits, and close-time teardown.

## Major Responsibilities

- Validate and checksum metadata tree blocks.
- Read extent buffers and retry alternate mirrors.
- Allocate, initialize, cache, and release Btrfs roots.
- Load global roots, filesystem roots, and important superblock roots.
- Initialize `btrfs_fs_info`, mount-time state, counters, locks, workqueues, and btree inode.
- Validate superblocks and feature compatibility.
- Execute `open_ctree()` mount flow.
- Write superblocks to all writable metadata devices.
- Execute `close_ctree()` shutdown flow.
- Clean up aborted transactions, dirty block groups, delayed refs, ordered extents, delalloc, pinned extents, and logs.
- Allocate new object IDs for roots.

## Metadata Checksum and Read Path

Key functions:

- `csum_tree_block()`: computes a checksum over a metadata tree block, skipping the checksum field itself.
- `btrfs_buffer_uptodate()`: checks whether an extent buffer is uptodate and matches the expected parent transid and optional parent check.
- `btrfs_check_super_csum()`: verifies a raw disk superblock checksum.
- `btrfs_read_extent_buffer()`: reads a tree block, retries mirrors on failure, and repairs a failed mirror after a successful alternate read.
- `btree_csum_one_bio()`: validates and checksums dirty metadata before writeback.
- `btrfs_validate_extent_buffer()`: performs read-time validation: bytenr, fsid, level, checksum, generation, first key, owner root, and leaf/node structural checks.
- `read_tree_block()`: allocates/fetches an extent buffer and reads it with required parentness checks.

## Btree Address-Space Operations

The file defines `btree_aops` for the special btree inode:

- `writepages = btree_writepages`
- `release_folio = btree_release_folio`
- `invalidate_folio = btree_invalidate_folio`
- `migrate_folio = btree_migrate_folio`
- `dirty_folio = btree_dirty_folio` in debug builds, otherwise `filemap_dirty_folio`

These operations enforce metadata-buffer lifetime rules and prevent unsafe migration or release while dirty/writeback state exists.

## Root Management

Important functions:

- `btrfs_alloc_root()`: allocates and initializes in-memory root structures, locks, lists, xarrays, refcounts, logging state, and per-root extent I/O trees.
- `btrfs_create_tree()`: creates a new tree root in a transaction and inserts its root item.
- `btrfs_read_tree_root()`: reads a root item and root node from the tree root.
- `btrfs_insert_fs_root()`: inserts a filesystem root into `fs_roots_radix`.
- `btrfs_get_fs_root()`: obtains a referenced global or filesystem root, loading from disk as needed.
- `btrfs_get_new_fs_root()`: same path for newly exposed roots with optional anonymous device handling.
- `btrfs_get_fs_root_commit_root()`: reads a temporary root from the commit root for backref/qgroup lookups.
- `btrfs_put_root()`: drops root references and frees root state.
- `btrfs_free_fs_roots()`: drops cached filesystem roots and dead roots.
- `btrfs_drop_and_free_fs_root()`: removes a root from the radix tree and drops the radix reference.

Global roots are stored in `fs_info->global_root_tree` and protected by `global_root_lock`. Helpers include:

- `btrfs_global_root_insert()`
- `btrfs_global_root_delete()`
- `btrfs_global_root()`
- `btrfs_csum_root()`
- `btrfs_extent_root()`

For extent-tree-v2, `btrfs_global_root_id()` maps a bytenr to a block group’s global root id.

## Log Tree Support

- `btrfs_init_log_root_tree()`: initializes the global log root tree.
- `btrfs_add_log_tree()`: creates a per-root log tree.
- `btrfs_replay_log()`: reads the log tree after mount and calls log recovery, committing the superblock if necessary for read-only replay cases.

## Mount-Time Initialization

`btrfs_init_fs_info()` initializes nearly all `fs_info` synchronization objects, lists, trees, counters, block reservations, work structures, discard control, reclaim state, qgroup state, scrub state, balance state, default sizes, and mount defaults.

`init_mount_fs_info()` attaches `fs_info` to the superblock, sets temporary block size values, initializes percpu counters, delayed root state, read-only/error flags, and stripe hash structures.

`btrfs_init_workqueues()` creates the main Btrfs workqueues, including workers for delalloc, flushing, caching, fixup, endio, metadata endio, read-modify-write, delayed metadata, qgroup rescan, and async discard.

## Superblock Validation

`btrfs_validate_super()` checks:

- magic value
- supported super flags
- root/chunk/log levels
- sectorsize and nodesize validity
- page-size support
- leafsize consistency
- root alignment
- fsid and metadata_uuid consistency
- device item fsid
- feature dependency rules for block-group-tree and remap-tree
- bytes used sanity
- stripesize
- device count
- super mirror bytenr
- system chunk array validity
- suspicious generation relationships

`btrfs_validate_write_super()` adds write-time checks for checksum type and incompat feature mask.

## Root Loading

- `load_super_root()` reads a root node directly from superblock bytenr/generation/level.
- `load_important_roots()` loads the tree root and optional remap root.
- `load_global_roots()` loads extent, csum, and optional free-space roots.
- `btrfs_read_roots()` loads block group, device, data reloc/remap, quota, UUID, RAID stripe, and related roots.

`init_tree_roots()` attempts normal root loading and, if configured, iterates backup root slots via `read_backup_root()`.

## `open_ctree()` Flow

`open_ctree()` is the primary mount entry point. Its high-level flow is:

1. Initialize mount `fs_info`.
2. Allocate tree and chunk roots.
3. Initialize the btree inode.
4. Read and checksum the disk superblock.
5. Copy superblock state into `super_copy` and `super_for_commit`.
6. Validate superblock and mount options.
7. Set filesystem block sizes and checksum parameters.
8. Initialize compression workspace and workqueues.
9. Read system chunk array and chunk tree.
10. Load tree roots and device/zone info.
11. Verify device items and device extents.
12. Recover balance/dev-replace/zoned/sysfs/space info/block groups.
13. Start cleaner and transaction kthreads.
14. Read qgroup config and optionally replay log.
15. Load the default filesystem root.
16. For writable mounts, run `btrfs_start_pre_rw_mount()`, resume async discard, and possibly rescan UUID tree.
17. Mark filesystem open.

The failure path unwinds sysfs, block groups, roots, workers, btree inode, and mapping tree in reverse order.

## Writable Mount Preparation

`btrfs_start_pre_rw_mount()` handles read-write setup shared by initial mount and remount:

- rebuilds or deletes free-space tree as requested
- removes orphan free-space tree entries
- finds orphan roots before orphan cleanup
- cleans filesystem roots and orphan items
- recovers relocation
- creates free-space tree if requested
- syncs v1 space cache setting
- resumes balance and device replace
- resumes qgroup rescan
- creates UUID tree if missing

## Background Threads

- `cleaner_kthread()`: delayed iputs, deleted snapshots, defrag, remap handling, unused block groups, and block group reclaim.
- `transaction_kthread()`: periodically commits transactions based on interval or explicit commit flag, and invokes transaction cleanup on errors.
- `btrfs_uuid_rescan_kthread()`: repairs/refreshes UUID tree entries.

## Superblock Write Path

- `backup_super_roots()`: rotates and fills backup root slots before transaction super writes.
- `write_dev_supers()`: writes one or more superblock mirrors to a device using direct bios, FUA for primary when barriers are enabled, and per-device error accounting.
- `wait_dev_supers()`: waits for submitted superblock writes and detects primary/all-copy failure.
- `barrier_all_devices()`: submits and waits for flushes across writable metadata devices.
- `write_all_supers()`: coordinates barriers, backup roots, per-device superblock contents, super validation, write submission, completion, and tolerated error thresholds.

## Shutdown and Cleanup

`close_ctree()` is a carefully ordered teardown path. It:

- marks closing start
- wakes unfinished drops
- cancels reclaim work
- parks cleaner
- waits for qgroup/UUID/balance/dev-replace/scrub/defrag activity
- handles aborted filesystem state
- flushes workqueues that may create delayed iputs or ordered completions
- runs delayed iputs
- cancels reclaim/shrinker works
- stops async discard
- commits the superblock unless read-only or shutdown
- stops transaction and cleaner threads
- frees qgroup config, sysfs, block groups, roots, workers, btree inode, and mapping tree

Transaction error cleanup is handled by:

- `btrfs_cleanup_transaction()`
- `btrfs_cleanup_one_transaction()`
- `btrfs_cleanup_dirty_bgs()`
- `btrfs_destroy_marked_extents()`
- `btrfs_destroy_pinned_extent()`
- `btrfs_destroy_all_ordered_extents()`
- `btrfs_destroy_all_delalloc_inodes()`
- `btrfs_drop_all_logs()`
- `btrfs_free_all_qgroup_pertrans()`

## Object ID Allocation

- `btrfs_init_root_free_objectid()` searches the root for the highest valid objectid and initializes `root->free_objectid`.
- `btrfs_get_free_objectid()` returns and increments the next free objectid under `objectid_mutex`.

## Integration Points

This file integrates with nearly every Btrfs subsystem: transactions, extent I/O, block groups, chunk/device mapping, free-space cache/tree, qgroups, UUID tree, dev-replace, zoned mode, relocation, scrub, compression, tree checker, sysfs, async discard, and tree logging.

## Risks and Invariants

- Metadata validation must reject stale, misplaced, wrong-owner, wrong-level, or corrupt tree blocks.
- Root reference counts and radix/global-tree insertion must stay balanced.
- Mount failure unwind order is critical to avoid leaked workers, roots, block groups, or btree inode pages.
- Superblock writes must respect degradability and primary-super failure rules.
- Shutdown order prevents workqueues from creating delayed iputs after cleaner teardown.
- Aborted transaction cleanup must unblock waiters and clear dirty/pinned metadata without relying on normal commit.
