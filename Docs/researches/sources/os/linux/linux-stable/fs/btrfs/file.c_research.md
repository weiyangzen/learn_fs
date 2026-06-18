# File Research: sources/os/linux/linux-stable/fs/btrfs/file.c

Btrfs regular-file VFS implementation and file extent mutation code. This file implements buffered writes, encoded/direct/buffered write dispatch, fsync/logging, mmap write faults, extent dropping and replacement, prealloc-to-written conversion, hole punching, fallocate, zero range, delalloc discovery, `SEEK_DATA`/`SEEK_HOLE`, open/read/splice/mmap hooks, and the exported `btrfs_file_operations` table.

Key responsibilities:
- Marks folios dirty through `btrfs_dirty_folio()`, setting delalloc state, uptodate/dirty bits, clearing checked state, handling `EXTENT_NORESERVE`, and extending in-memory `i_size`.
- Drops or rewrites file extent items in `btrfs_drop_extents()`, handling full deletion, front/back truncation, middle splits, inline extent rejection, delayed ref updates, extent-map cache invalidation, and optional replacement-item setup.
- Converts preallocated extents to written regular extents in `btrfs_mark_extent_written()`, including splitting, merging adjacent compatible extents, delayed ref updates, generation changes, and file extent range tracking.
- Prepares folios for buffered writes, reads partial blocks when required, locks ranges, waits ordered extents, and retries when folios are invalidated or ordered I/O overlaps.
- Checks NOCOW write eligibility with `btrfs_check_nocow_lock()`, using the root snapshot lock and ordered-range flushing/try-locking before calling `can_nocow_extent()`.
- Performs common write preflight in `btrfs_write_check()`, including NOWAIT COW rejection, privilege stripping, timestamp/version updates, and hole expansion before writes past EOF.
- Reserves and releases data/metadata space for buffered writes, including metadata-only reservations for NOCOW fallback.
- Dispatches encoded, direct, and buffered writes from `btrfs_do_write_iter()`, rejecting writes during shutdown or filesystem error states and running write sync when needed.
- Implements `btrfs_sync_file()` for files and directories using tree logging when possible and transaction commit fallback when required.
- Handles mmap write faults in `btrfs_page_mkwrite()`, reserving delalloc before folio lock, handling EOF/truncate races, waiting ordered extents, zeroing partial EOF, and marking delalloc/dirty state.
- Inserts or merges explicit hole extent items in `fill_holes()` for filesystems without `NO_HOLES`, and installs hole extent maps or forces full fsync when extent-map insertion fails.
- Replaces file extents with holes or supplied replacement metadata through `btrfs_replace_file_extents()`.
- Implements hole punching, fallocate preallocation, zero range, delalloc/ordered range discovery, and `SEEK_DATA`/`SEEK_HOLE`.

Important data flows:
- Buffered write path: `btrfs_file_write_iter()` calls `btrfs_do_write_iter()`, which selects `btrfs_buffered_write()` unless direct or encoded I/O is requested. `btrfs_buffered_write()` locks the inode, runs generic and Btrfs write checks, then loops through `copy_one_range()` to reserve space, fault user pages, prepare a folio, wait conflicting ordered extents, copy bytes, mark delalloc, and release reservations.
- NOCOW reservation path: `reserve_space()` first tries normal data reservation. On reservation failure, it may call `btrfs_check_nocow_lock()` and reserve metadata only, with cleanup through `release_space()` or `shrink_reserved_space()`.
- Extent drop path: `btrfs_drop_extents()` searches file extent items around the requested range, adjusts overlapping regular/prealloc extents, rejects partial inline changes, deletes covered items in batches, updates delayed refs and bytes-found accounting, and may pre-create space for a replacement item.
- Fsync path: `btrfs_sync_file()` widens every fsync to the full file range, starts writeback before locking, locks inode plus mmap state, starts writeback again for concurrent dirties, then either waits ordered extents for full sync/zoned filesystems or gathers ordered extents for fast logging. It logs the dentry, syncs the log if possible, or commits a transaction on fallback.
- Mmap fault path: `btrfs_page_mkwrite()` reserves before folio locking to avoid writeback deadlocks, locks `i_mmap_lock`, locks the folio and io_tree range, waits ordered extents, clips to EOF, marks delalloc, sets dirty/uptodate bits, and returns the folio locked.
- Hole punching path: `btrfs_fallocate()` routes `FALLOC_FL_PUNCH_HOLE` to `btrfs_punch_hole()`, which zeros unaligned boundaries, waits ordered extents, locks and evicts page cache for the aligned range, calls `btrfs_replace_file_extents()` without replacement metadata, and updates inode metadata.
- Fallocate/zero-range path: `btrfs_zero_range()` avoids work when the target is already preallocated, handles unaligned boundary blocks, reserves data/qgroup space, locks the clean aligned range, uses preallocation, and updates `i_size`. `btrfs_fallocate()` scans extent maps to build coalesced ranges needing allocation.
- Seek path: `btrfs_file_llseek()` calls `find_desired_extent()`, which locks the searched io_tree range, walks file extent items, treats prealloc and explicit holes as holes, detects implicit holes, and overlays delalloc/ordered ranges so dirty data is reported as data.

Concurrency and locking:
- Buffered writes take the Btrfs inode lock, using `BTRFS_ILOCK_TRY` for NOWAIT.
- Write preparation locks folios and io_tree ranges and drops them to wait ordered extents when conflicts are found.
- NOCOW checks hold `root->snapshot_lock` in write mode on success; callers must release it with `btrfs_check_nocow_unlock()`.
- Fsync starts writeback outside inode lock, then locks inode plus `i_mmap_lock` to stabilize logging state.
- Hole punching and fallocate take inode and mmap locks exclusively, wait ordered extents, lock aligned io_tree ranges, and assert the target range is clean before metadata mutation.
- `btrfs_punch_hole_lock_range()` repeatedly truncates page cache, locks the io_tree range, and rechecks for folios to avoid racing page faults/reads.
- Per-file llseek cached state is stored in `file->private_data`, guarded during installation by `inode->lock`, and reused only by the owning task.

Important invariants:
- File extent item ranges and file extent presence tracking are sector aligned.
- `btrfs_drop_extents()` reports allocated bytes removed through `args->bytes_found`; callers update inode byte counts atomically with replacement/removal.
- Partial inline extent replacement/drop is unsupported and returns `-EOPNOTSUPP`.
- `btrfs_replace_file_extents()` returns an open transaction through `trans_out` on success; callers must finish inode updates and end the transaction.
- Explicit hole items are inserted only when `NO_HOLES` is disabled or replacement logic requires an item; otherwise file extent tracking is cleared.
- Fallocate is rejected on zoned filesystems.
- Fast fsync correctness depends on full-file range consideration, ordered extent checksum handling, and hole extent maps; failures to install hole maps force full sync.
- `SEEK_HOLE` can return `i_size` quickly only when the inode has no prealloc extents and allocated bytes equal `i_size`.
- `btrfs_fdatawrite_range()` intentionally performs a second writeback pass when async compression has staged extents but not yet marked pages writeback.

Notable risks:
- `btrfs_drop_extents()` and `btrfs_mark_extent_written()` mutate B-tree items, delayed refs, extent-map cache, inode byte accounting, and file extent presence state in tightly coupled sequences.
- Buffered write cleanup has many branches for data reservations, metadata reservations, NOCOW metadata-only state, extent locks, folio references, and cached extent states.
- Mmap write faults reserve before folio locking, so all error paths must release the correct reservation type and possibly the NOCOW snapshot lock.
- Fsync deliberately widens the requested range; narrowing it would risk missing holes, checksums, or ordered extents.
- `btrfs_replace_file_extents()` restarts transactions inside a loop, so callers must tolerate partial progress and repeated inode timestamp/version updates.
- Large folio handling in hole punching avoids false positives from generic page-cache range checks; future page-cache changes must preserve the head/tail folio assumptions.
