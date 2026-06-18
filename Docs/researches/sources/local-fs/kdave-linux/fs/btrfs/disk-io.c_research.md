# File Research: sources/local-fs/kdave-linux/fs/btrfs/disk-io.c

## Role

Large Btrfs core file for metadata I/O, superblock validation/writes, root allocation and lookup, mount initialization, unmount teardown, transaction cleanup, and metadata dirty throttling. It is the coordination layer that brings together devices, roots, block groups, workqueues, log replay, qgroups, discard, zoned mode, and cleaner/transaction kthreads.

## Metadata Checksum and Tree-Block I/O

- `csum_tree_block()` calculates the checksum for a tree block over all extent-buffer pages or the contiguous buffer mapping.
- `btrfs_buffer_uptodate()` validates an already-cached extent buffer against parent transid and optional parentness checks.
- `btrfs_supported_super_csum()` accepts CRC32C, XXHASH, SHA256, and BLAKE2 superblock checksum types.
- `btrfs_check_super_csum()` verifies the superblock checksum over the full 4 KiB superblock area after the checksum field.
- `btrfs_read_extent_buffer()` reads an extent buffer with mirror retry. If a bad mirror is found and another mirror succeeds, it attempts repair through `btrfs_repair_eb_io_failure()`.
- `btree_csum_one_bio()` validates and writes a dirty tree block checksum before metadata write I/O. It also detects write-time tree block corruption, bad generation, wrong bytenr, and zoned zeroout buffers.
- `btrfs_validate_extent_buffer()` performs read-time validation: bytenr, FSID/metadata UUID or seed FSID, level, checksum, parent transid, first key, owner root, and node/leaf structural checks.
- `read_tree_block()` allocates/fetches an extent buffer and reads it with the provided `btrfs_tree_parent_check`.

## Btree Address-Space Operations

- `btree_release_folio()` refuses to release dirty or writeback metadata folios and delegates to `try_release_extent_buffer()`.
- `btree_invalidate_folio()` invalidates extent I/O state and warns if private state remains.
- `btree_migrate_folio()` is available under migration support and refuses migration for dirty or privately pinned metadata folios.
- Debug `btree_dirty_folio()` verifies dirty extent-buffer invariants for normal and subpage metadata before marking the folio dirty.
- `btree_aops` wires metadata writeback, folio release, invalidation, migration, and dirtying behavior for the internal btree inode.

## Root Allocation, Lookup, and Lifetime

- `btrfs_alloc_root()` initializes an in-memory root: xarrays, reservation structures, delalloc/ordered/log lists, locks, waitqueues, qgroup state, log counters, references, and debug leak tracking.
- `btrfs_create_tree()` allocates a new tree root, creates its initial leaf, initializes root item fields and UUID, inserts it into the tree root, and returns the new root.
- `alloc_log_tree()`, `btrfs_alloc_log_tree_node()`, `btrfs_init_log_root_tree()`, and `btrfs_add_log_tree()` create log-tree roots and per-subvolume log roots.
- `read_tree_root_path()` reads a root item from the tree root, loads its root node, validates generation/owner, and sets `commit_root`.
- `btrfs_read_tree_root()` is the public wrapper around `read_tree_root_path()`.
- `btrfs_init_fs_root()` initializes user-visible filesystem roots, assigns anonymous block devices, marks shareable roots, and seeds `free_objectid`.
- `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, and `btrfs_get_fs_root_commit_root()` retrieve root references from global roots, the radix cache, or disk.
- `btrfs_insert_fs_root()`, `btrfs_drop_and_free_fs_root()`, `btrfs_free_fs_roots()`, and `btrfs_put_root()` manage radix-tree membership and root references.
- `btrfs_global_root_insert()`, `btrfs_global_root_delete()`, `btrfs_global_root()`, `btrfs_csum_root()`, and `btrfs_extent_root()` manage the global-root rb-tree used by extent tree v2 and per-global-id roots.

## Superblock and Backup Root Handling

- `find_newest_super_backup()`, `backup_super_roots()`, and `read_backup_root()` maintain the rotating superblock backup root array.
- `validate_sys_chunk_array()` validates the system chunk array embedded in the superblock.
- `btrfs_validate_super()` performs mount/write-time structural validation of magic, flags, root levels, sectorsize, nodesize, alignment, FSID/metadata UUIDs, feature dependencies, bytes-used sanity, stripesize, device count, superblock bytenr, system chunks, and suspicious generation relationships.
- `btrfs_validate_mount_super()` validates the mounted superblock mirror.
- `btrfs_validate_write_super()` repeats super validation before write and additionally validates checksum type and incompat flags.
- `write_dev_supers()` writes superblock mirrors to a device with direct bios and FUA for the primary mirror when barriers are enabled.
- `wait_dev_supers()` waits for submitted superblock writes and treats primary mirror failure specially.
- `write_dev_flush()`, `wait_dev_flush()`, and `barrier_all_devices()` issue and wait for device flushes across writable metadata devices.
- `write_all_supers()` coordinates pre-super barriers, backup root update, per-device dev item population, superblock validation, writes, and wait/error accounting.

## Mount Initialization

`open_ctree()` is the full mount path:

- Initializes `fs_info` counters and root structures, creates the internal btree inode, reads the latest device superblock, validates checksum type and checksum value, and copies it to `super_copy` and `super_for_commit`.
- Validates the superblock, initializes checksum, nodesize, sectorsize, block orders, csum geometry, free-space cache settings, mount options, and feature compatibility.
- Allocates compression workspace and all major workqueues, adjusts readahead, reads the system array, loads chunk root, reads the chunk tree, and frees extra device IDs.
- Loads important roots and global roots, with backup-root retry support when requested.
- Initializes zoned device information, verifies device items and extents, recovers balance state, initializes device stats and device replacement, initializes sysfs, space info, and block groups.
- Starts the cleaner and transaction kthreads, reserves zoned data relocation block groups, reads qgroup config, optionally builds the reference verification tree, replays the log tree when required, and loads the default filesystem tree.
- For read-write mounts, calls `btrfs_start_pre_rw_mount()`, resumes async discard, optionally checks/rescans the UUID tree, sets `BTRFS_FS_OPEN`, and wakes the cleaner for unfinished drops.
- Error labels unwind initialized kthreads, qgroups, sysfs, block groups, roots, workqueues, mapping trees, and the btree inode in reverse order.

## Read-Write Mount Preparation

`btrfs_start_pre_rw_mount()` performs rw-only recovery and format maintenance:

- Rebuilds, deletes, or creates the free-space tree based on mount options and on-disk validity.
- Deletes orphan free-space-tree entries left by older mkfs behavior.
- Finds orphan roots before orphan cleanup so pending deleted subvolumes are not lost.
- Cleans cached filesystem roots and root/tree orphans.
- Recovers relocation, synchronizes space-cache v1 activation, resumes balance and device replace, resumes qgroup rescan, and creates the UUID tree if absent.

## Feature and Runtime Checks

- `btrfs_check_features()` rejects unsupported incompat features and rw mounts with unsupported compat-ro features, blocks unsafe log replay with unsupported compat-ro flags, enforces mixed-group sectorsize/nodesize constraints, sets always-enabled and compression-related incompat flags, enforces block-group-tree and space-cache dependencies, and rejects v1 space cache for subpage sectorsize.
- `fs_is_full_ro()` detects rescue/full-read-only mount modes that must prevent transactions.

## Kthreads and Workqueues

- `cleaner_kthread()` runs delayed iputs, deleted snapshot cleanup, defrag work, fully remapped block-group handling when async discard is off, unused block-group deletion, and block-group reclaim. It parks/stops cooperatively and updates `BTRFS_FS_CLEANER_RUNNING`.
- `transaction_kthread()` periodically commits the running transaction based on `commit_interval` or explicit commit requests, wakes the cleaner, and invokes transaction cleanup on filesystem errors.
- `btrfs_init_workqueues()` creates worker, delalloc, flush, cache, fixup, endio, metadata endio, rmw, freespace, delayed metadata, qgroup rescan, and discard workqueues.
- `btrfs_stop_all_workers()` destroys those queues in an order that preserves metadata I/O safety until dependent queues are gone.

## Unmount and Error Cleanup

- `close_ctree()` begins closing, wakes unfinished drops, cancels reclaim, parks the cleaner, waits for qgroup/UUID tasks, pauses balance, suspends dev-replace, cancels scrub, waits for defrag, handles error cleanup, flushes workqueues in an order that prevents delayed iputs after kthread destruction, cancels reclaim/shrinker work, runs delayed iputs, disables new delayed iputs, cleans up async discard, deletes unused block groups, flushes delayed workers, commits the superblock when appropriate, stops kthreads, frees qgroups, removes sysfs, drops block-group cache, checks uncommitted transactions, frees roots, invalidates btree inode pages, stops workers, frees block groups, releases the btree inode, and frees the mapping tree.
- `btrfs_error_commit_super()` runs transaction cleanup and waits on cleanup work for aborted filesystems.
- `btrfs_cleanup_transaction()` walks all transactions, waits for those already committing, cleans pending ones, destroys ordered extents, delayed inodes, delalloc inodes, logs, and per-transaction qgroup state.
- `btrfs_cleanup_one_transaction()` cleans dirty block groups, delayed refs, dirty metadata extents, pinned extents, and wakes commit waiters.
- `btrfs_cleanup_dirty_bgs()` handles dirty and I/O block-group lists, marks disk cache state error, drops refs, and cleans up free-space cache inode I/O.
- `btrfs_destroy_marked_extents()` and `btrfs_destroy_pinned_extent()` clear transaction extent-state trees during abort/error cleanup.

## Miscellaneous Operations

- `btrfs_init_fs_info()` initializes almost every lock, list, rb-tree, radix/xarray, waitqueue, reservation, default option, counter, and subsystem state in `fs_info`.
- `init_mount_fs_info()` initializes mount-time percpu counters, delayed root, read-only/error state bits, and stripe hash table.
- `btrfs_check_uuid_tree()` starts a UUID tree rescan kthread after taking the rescan semaphore.
- `btrfs_commit_super()` runs delayed iputs, waits for cleanup work, and commits the current transaction.
- `btrfs_mark_buffer_dirty()` asserts transaction/generation correctness before setting an extent buffer dirty.
- `btrfs_btree_balance_dirty()` and `btrfs_btree_balance_dirty_nodelay()` throttle dirty metadata through `balance_dirty_pages_ratelimited()`.
- `btrfs_init_root_free_objectid()` searches the root for the highest object ID and seeds the next free object ID.
- `btrfs_get_free_objectid()` returns and increments a root's free object ID under `objectid_mutex`.
- `btrfs_get_num_tolerated_disk_barrier_failures()` computes the minimum tolerated flush failure count across RAID profiles.

## Dependencies

This file depends on nearly every major Btrfs subsystem: transactions, inode state, delayed inodes, bios, tree locking/checking, free-space cache/tree, dev-replace, RAID56, sysfs, qgroups, compression, ref verification, block groups, discard, space info, zoned mode, subpage metadata, extent tree, root tree, defrag, UUID tree, relocation, scrub, and superblock helpers. It also binds to Linux VFS, block-device, writeback, kthread, workqueue, migration, checksum, UUID, semaphore, and error-injection APIs.

## Research Notes

`disk-io.c` is not just disk I/O. It is the mount lifecycle orchestrator and the point where Btrfs validates durable metadata before trusting it. Its most important behavior is ordering: validation before root loading, device/chunk setup before logical tree I/O, kthreads before transactions, rw recovery before opening, and a very deliberate teardown sequence to avoid delayed iput, ordered extent, workqueue, and transaction races during unmount or abort.
