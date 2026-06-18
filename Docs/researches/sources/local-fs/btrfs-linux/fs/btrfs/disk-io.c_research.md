# File Research: sources/local-fs/btrfs-linux/fs/btrfs/disk-io.c

## Summary
Implements core Btrfs disk I/O, metadata block validation, root loading/caching, mount and unmount orchestration, superblock writing, background kthreads, workqueue setup, and transaction cleanup after errors.

## Main Responsibilities
- Validate and checksum metadata extent buffers and superblocks.
- Read tree blocks with mirror retry and repair failed mirror reads.
- Allocate, load, cache, reference, and free Btrfs roots.
- Initialize `btrfs_fs_info`, btree inode, worker pools, qgroup/scrub/balance/discard state.
- Execute the main mount flow in `open_ctree()`.
- Execute read-write mount preparation in `btrfs_start_pre_rw_mount()`.
- Write all superblock mirrors with barriers/FUA handling.
- Shut down the filesystem in `close_ctree()`.
- Clean up aborted or uncommitted transactions.

## Key APIs
- Metadata I/O: `read_tree_block()`, `btrfs_read_extent_buffer()`, `btrfs_validate_extent_buffer()`, `btree_csum_one_bio()`, `btrfs_buffer_uptodate()`.
- Superblock validation/writes: `btrfs_check_super_csum()`, `btrfs_validate_super()`, `write_all_supers()`, `btrfs_commit_super()`.
- Root management: `btrfs_read_tree_root()`, `btrfs_insert_fs_root()`, `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, `btrfs_get_fs_root_commit_root()`, `btrfs_put_root()`, `btrfs_drop_and_free_fs_root()`, `btrfs_free_fs_roots()`.
- Global roots: `btrfs_global_root_insert()`, `btrfs_global_root_delete()`, `btrfs_global_root()`, `btrfs_csum_root()`, `btrfs_extent_root()`.
- Mount lifecycle: `btrfs_init_fs_info()`, `btrfs_start_pre_rw_mount()`, `open_ctree()`, `close_ctree()`.
- Dirty metadata: `btrfs_mark_buffer_dirty()`, `btrfs_btree_balance_dirty()`, `btrfs_btree_balance_dirty_nodelay()`.
- Transaction cleanup: `btrfs_cleanup_dirty_bgs()`, `btrfs_cleanup_one_transaction()`.

## Important Behavior
Metadata read validation checks bytenr, fsid/metadata UUID, tree level, checksum, parent transid, first key, owner root, and node/leaf structural consistency. Failed reads can retry alternate mirrors; successful retry after a failed mirror attempts metadata repair.

Write-time metadata checksum through `btree_csum_one_bio()` verifies the extent buffer bytenr, uptodate state, fsid, node/leaf structure, and generation relative to the last committed transaction before writing the checksum.

Root management distinguishes essential/global trees from subvolume roots. Global roots use an rb-tree keyed by root key, while subvolume roots are cached in `fs_roots_radix`. Extent tree v2 uses block-group `global_root_id` to select per-global extent and csum roots.

`open_ctree()` is the central mount sequence. It initializes counters and roots, reads and validates the primary superblock, parses features/options, initializes compression and workers, reads system chunks and chunk tree, loads important roots and all global roots, verifies devices and extents, initializes block groups, sysfs, qgroups, dev-replace, zoned mode, cleaner/transaction kthreads, log replay, fs root loading, read-write mount preparation, async discard resume, and UUID-tree checking.

`btrfs_start_pre_rw_mount()` handles rw-only preparation: free-space-tree rebuild/delete/create, orphan free-space cleanup, orphan root discovery, orphan cleanup, relocation recovery, balance/dev-replace resume, qgroup rescan resume, and UUID-tree creation.

Superblock writes use per-device direct bios rather than page-cache writeback. Transaction commits write all mirrors and update backup roots; fsync-like callers write only the primary mirror. Barriers are sent to all writable metadata devices first unless disabled. The primary superblock gets FUA when barriers are enabled.

`close_ctree()` is carefully ordered. It wakes unfinished drops, stops reclaim and parks cleaner, waits for qgroup/UUID/balance/dev-replace/scrub/defrag work, handles error commits, flushes workqueues that can create delayed iputs or ordered completions, runs delayed iputs, cancels reclaim and discard work, optionally commits the final superblock, stops kthreads, checks leaks/counters, removes sysfs, drops roots/block groups, invalidates btree inode pages, stops workers, and frees mapping state.

## State and Synchronization
Major state lives in `btrfs_fs_info`: roots, global root rb-tree, fs-root radix tree, transaction lists, block reservations, workqueues, block-group trees, delayed iputs, ordered roots, discard control, qgroup/scrub/balance/dev-replace state, sysfs state, and mount flags.

The cleaner kthread performs delayed iputs, deleted snapshot cleanup, defrag, fully remapped block-group handling, unused block-group deletion, and block-group reclaim. The transaction kthread commits based on interval or explicit commit requests and performs cleanup when the filesystem is aborted.

Locking spans spinlocks for radix/list state, rwlocks for global roots and tree-mod log, mutexes for transactions, cleaner, chunk, relocation, qgroup, block-group reclaim, and semaphores/rwsems for cleanup, commits, subvolumes, and UUID rescans.

## Risks
Mount error unwinding is high risk because each initialization phase has different ownership: roots, btree inode, worker pools, sysfs, block groups, mapping tree, devices, qgroups, and kthreads must be unwound in the right order.

Metadata validation is strict and central to corruption detection. Any missed check can admit bad tree blocks; any over-strict check can reject recoverable filesystems.

Unmount ordering is fragile because workqueues, ordered extents, delayed iputs, reclaim workers, and cleaner/transaction kthreads can wake or depend on each other.

Superblock writing must tolerate missing devices according to RAID/degradability rules while treating primary superblock failure specially.

Transaction cleanup forcibly errors ordered extents, destroys delayed refs/inodes, dirty metadata, pinned extents, block-group I/O state, and logs. Mistakes here can leak reservations or leave waiters blocked.
