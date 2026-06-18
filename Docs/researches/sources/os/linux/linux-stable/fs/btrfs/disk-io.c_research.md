# File Research: sources/os/linux/linux-stable/fs/btrfs/disk-io.c

## Purpose
Central Btrfs mount, metadata IO, root management, superblock write, transaction cleanup, and unmount implementation. This file wires together filesystem startup and teardown with tree-block validation, root caches, worker queues, feature checks, log replay, block-group loading, discard lifecycle, and final error cleanup.

## Metadata Block IO And Validation
- `csum_tree_block()` computes metadata block checksums over an extent buffer, handling contiguous and multi-folio buffers.
- `btrfs_buffer_uptodate()` validates cached extent buffers against parent transid and optional parent/key/owner checks.
- `btrfs_read_extent_buffer()` reads metadata, retries alternate mirrors on failure, and repairs failed mirror reads with `btrfs_repair_eb_io_failure()` when possible.
- `btree_csum_one_bio()` verifies dirty metadata before write: block address, uptodate state, fsid, structural tree checker result, and generation newer than last committed. It writes the checksum only after validation.
- `btrfs_validate_extent_buffer()` performs read-time validation: bytenr, fsid/metadata UUID, level, checksum unless ignored, parent transid, first key, owner root, and leaf/node checker.

## Address-Space And Extent Buffer Integration
- Defines `btree_aops` for the btree inode: `btree_writepages`, folio release, invalidation, migration, and debug dirty-folio checking.
- `btrfs_find_create_tree_block()` allocates normal or test extent buffers.
- `read_tree_block()` allocates/looks up an extent buffer and reads it with strict parent checks.

## Root Allocation, Caching, And Lookup
- `btrfs_alloc_root()` initializes `struct btrfs_root`: xarrays, reservations, lists, locks, log state, qgroup state, refcount, and debug leak tracking.
- Global roots are stored in `fs_info->global_root_tree` with `btrfs_global_root_insert()`, `btrfs_global_root_delete()`, and `btrfs_global_root()`.
- `btrfs_global_root_id()` maps bytenr to a global-root index for extent-tree-v2 via block-group `global_root_id`.
- `btrfs_csum_root()` and `btrfs_extent_root()` select global checksum/extent roots for a bytenr.
- `btrfs_create_tree()` creates a new on-disk tree root item and initializes its first leaf.
- Log trees are allocated by `alloc_log_tree()`, `btrfs_alloc_log_tree_node()`, `btrfs_init_log_root_tree()`, and `btrfs_add_log_tree()`.
- `read_tree_root_path()` and `btrfs_read_tree_root()` read root items from the tree root, validate their root nodes, and enforce owner consistency for normal roots.
- `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, and `btrfs_get_fs_root_commit_root()` serve cached/global/subvolume roots with reference management and anon-bdev setup for exposed subvolumes.
- `btrfs_put_root()`, `btrfs_drop_and_free_fs_root()`, `btrfs_free_fs_roots()`, and `btrfs_free_fs_info()` release root and fs-wide resources.

## Mount-Time Threads And Workers
- `cleaner_kthread()` runs delayed iputs, deleted snapshot cleanup, defrag, fully remapped block group handling when async discard is off, unused block group deletion, and block group reclaim.
- `transaction_kthread()` periodically commits the running transaction based on commit interval or explicit commit requests.
- `btrfs_init_workqueues()` creates Btrfs worker pools, including the ordered `btrfs-discard` workqueue stored in `fs_info->discard_ctl.discard_workers`.
- `btrfs_stop_all_workers()` destroys all worker queues, including discard, after higher-level users have been stopped.

## Superblock And Root Loading
- `btrfs_check_super_csum()` validates superblock checksum after checksum type has been established.
- `btrfs_validate_super()` checks magic, flags, levels, sector/node size, alignment, fsid/metadata UUID, feature dependencies, remap-tree constraints, bytes-used sanity, stripesize, device count, super offset, system chunk array, and generation warnings.
- `validate_sys_chunk_array()` parses and validates the embedded system chunk array.
- Backup root handling is implemented by `find_newest_super_backup()`, `backup_super_roots()`, and `read_backup_root()`.
- `load_super_root()`, `load_important_roots()`, `load_global_roots_objectid()`, `load_global_roots()`, `btrfs_read_roots()`, and `init_tree_roots()` load tree, chunk, remap, extent, checksum, free-space, block-group, device, relocation, quota, UUID, stripe, and other roots with backup-root fallback when requested.

## Filesystem Initialization
- `btrfs_init_fs_info()` initializes nearly all in-memory fs-wide state: radix/xarray/rbtree roots, locks, waitqueues, transaction state, reservations, reclaim state, scrub/balance/qgroup/dev-replace state, extent IO trees, defaults, and async discard state via `btrfs_discard_init()`.
- `init_mount_fs_info()` binds the superblock, initializes percpu counters, delayed root, read-only/error state bits, and stripe hash table.
- `open_ctree()` is the main mount path:
  - Initializes `fs_info`, root objects, btree inode, superblock checksum and validation.
  - Sets sector/node/checksum sizes, mount options, feature flags, compression workspaces, and workers.
  - Reads system array, chunk root/tree, device and zone information, tree roots, block groups, sysfs, space info, qgroups, and logs.
  - Replays the tree log unless disabled, reads the default fs tree, runs writable mount setup, resumes async discard with `btrfs_discard_resume()`, checks UUID tree, marks the filesystem open, and wakes cleaner for unfinished drops.
  - Has structured failure labels that unwind workers, sysfs, block groups, roots, mappings, and btree inode state.

## Writable Mount Preparation
`btrfs_start_pre_rw_mount()` handles read-write-only setup:
- Rebuilds, deletes, or creates the free-space tree based on options and on-disk validity.
- Deletes orphan free-space tree entries from older mkfs behavior.
- Finds orphan roots before orphan cleanup to preserve pending deleted-root semantics.
- Cleans orphan items, recovers relocation, resumes balance/dev-replace/qgroup rescan, toggles v1 space cache, and creates UUID tree if missing.

## Feature Checks
`btrfs_check_features()` rejects unknown incompat features, unsupported read-write compat_ro features, dirty log replay with unsupported compat_ro features, mixed block groups with unequal sectorsize/nodesize, block-group-tree without required no-holes/free-space-tree settings, and v1 space cache on unsupported subpage configurations. It also normalizes always-on or implied incompat flags in the super copy.

## Superblock Writes And Barriers
- `write_dev_supers()` writes one or more superblock mirrors per writable metadata device using direct bios and FUA for the primary mirror unless barriers are disabled.
- `wait_dev_supers()` waits for submitted super writes and treats primary-super failure specially.
- `write_dev_flush()`, `wait_dev_flush()`, and `barrier_all_devices()` submit and collect device flushes, checking degradability after errors.
- `write_all_supers()` prepares backup roots, updates per-device `dev_item`, validates the superblock before each write, submits all device super writes, waits for them, and aborts the transaction if error tolerance is exceeded.

## Unmount And Error Cleanup
- `close_ctree()` performs ordered shutdown: set closing state, wake unfinished drops, stop reclaim, park cleaner, wait qgroup/UUID/scrub/defrag, handle error commit cleanup, flush all workqueues that can create delayed iputs or ordered extents, cancel reclaim/shrinker work, disable delayed iputs, cleanup discard with `btrfs_discard_cleanup()`, delete unused block groups, commit final super if needed, stop kthreads, free qgroups/sysfs/block groups/roots/workers/mapping tree, and release the btree inode.
- `btrfs_error_commit_super()` invokes transaction cleanup under cleanup-work synchronization for errored filesystems.
- `btrfs_cleanup_transaction()` cleans all non-committed transactions, ordered extents, delayed inodes, delalloc inodes, logs, and qgroup per-transaction reservations.
- `btrfs_cleanup_one_transaction()` cleans dirty block groups, delayed refs, dirty metadata extent states, pinned extents, and wakes transaction waiters.
- `btrfs_cleanup_dirty_bgs()` marks dirty block group cache IO as errored and releases references.
- `btrfs_destroy_marked_extents()` and `btrfs_destroy_pinned_extent()` use `extent-io-tree.c` helpers to clear dirty/pinned state and release extent buffers or unpin extents.

## Object ID Management
- `btrfs_init_root_free_objectid()` searches the root for the highest valid objectid and initializes `root->free_objectid`.
- `btrfs_get_free_objectid()` allocates monotonically increasing objectids under `root->objectid_mutex`, returning `-ENOSPC` at the upper limit.

## Relationship To This Group
- Owns discard subsystem initialization, workqueue allocation/destruction, mount resume, and unmount cleanup.
- Uses extent IO trees for dirty transaction pages, pinned extents, btree inode IO, root log dirty pages, and cleanup iteration.
- Supplies root lookup used by export support through `btrfs_get_fs_root()`.
