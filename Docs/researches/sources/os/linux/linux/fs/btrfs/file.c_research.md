# File Research: sources/os/linux/linux/fs/btrfs/file.c

Btrfs regular-file VFS implementation and file extent mutation code. This file implements buffered writes, write validation and dispatch, fsync/logging, mmap write faults, extent dropping and replacement, hole punching, fallocate and zero range, delalloc discovery, SEEK_DATA/SEEK_HOLE, open/read/splice/mmap hooks, and the exported `btrfs_file_operations` table.

Key responsibilities:
- Marks folios dirty for buffered writes through `btrfs_dirty_folio()`, including delalloc state, folio uptodate/dirty bits, checked-bit clearing, `EXTENT_NORESERVE`, and in-memory i_size extension.
- Drops or rewrites file extent items with `btrfs_drop_extents()`, handling full deletion, front/back truncation, middle split, inline extent rejection, reference updates, extent-map cache dropping, and optional replacement item setup.
- Converts preallocated extents to written regular extents with `btrfs_mark_extent_written()`, including splitting into multiple file extent items, merging adjacent compatible written extents, delayed ref updates, generation updates, and file extent range tracking.
- Prepares folios for buffered writes, reads partial blocks when required, sets extent mapping private data, locks ranges, waits for ordered extents, and retries when folios are invalidated or ordered I/O overlaps.
- Probes NOCOW write eligibility with `btrfs_check_nocow_lock()`, using the root snapshot lock, ordered-range flushing or try-locking, and `can_nocow_extent()` over the candidate range.
- Performs common write validation in `btrfs_write_check()`, including NOWAIT COW rejection, privilege stripping, time/version updates, and hole expansion before writes past EOF.
- Reserves and releases data/metadata space for buffered writes, including metadata-only reservations for NOCOW fallback and careful shrinking after short copies or folio-boundary clipping.
- Implements the buffered write loop through `btrfs_buffered_write()` and `copy_one_range()`, copying at most one folio-sized chunk per iteration and updating `ki_pos` only after successful bytes are copied.
- Dispatches encoded, direct, and buffered writes from `btrfs_do_write_iter()`, rejects writes during shutdown or filesystem error state, and performs generic write sync after successful data writes.
- Cleans per-file private state and flush-on-close state in `btrfs_release_file()`.
- Implements `btrfs_sync_file()` for file and directory fsync, using tree logging when possible and transaction commit fallback when required.
- Implements mmap write faults through `btrfs_page_mkwrite()`, reserving delalloc space before taking the folio lock to avoid writeback deadlocks, handling EOF/truncate races, waiting ordered extents, zeroing partial EOF, and setting delalloc/dirty state.
- Inserts or merges explicit hole extent items in `fill_holes()` for filesystems without `NO_HOLES`, and installs hole extent maps or forces full fsync when extent-map insertion fails.
- Replaces file extents through `btrfs_replace_file_extents()`, used by hole punching and clone/dedupe-style replacement, with transaction restart handling and optional replacement extent insertion.
- Implements `btrfs_punch_hole()`, including unaligned head/tail zeroing, ordered extent waits, range locking with page-cache eviction, file extent replacement, inode timestamp/version updates, and transaction completion.
- Implements `btrfs_fallocate()` and `btrfs_zero_range()`, including qgroup/data reservations, preallocation range coalescing, keep-size behavior, i_size updates, zoned rejection, and optimized handling of already preallocated ranges.
- Finds delalloc and ordered subranges with `btrfs_find_delalloc_in_range()` and uses this to implement correct `SEEK_DATA`/`SEEK_HOLE` over explicit extents, implicit holes, prealloc extents, and dirty ranges.
- Defines regular-file read, splice, open, mmap, llseek, fsync, fallocate, ioctl, remap, io_uring command, and lease operations in `btrfs_file_operations`.
- Provides `btrfs_fdatawrite_range()`, including a second writeback pass when async compression has staged extents but not yet marked pages writeback.

Important data flows:
- Buffered write path: `btrfs_file_write_iter()` calls `btrfs_do_write_iter()`, which selects `btrfs_buffered_write()` unless direct or encoded I/O is requested. `btrfs_buffered_write()` locks the inode, runs generic checks and `btrfs_write_check()`, then repeatedly calls `copy_one_range()` to reserve space, fault user pages, prepare a folio, wait conflicting ordered extents, copy data, mark delalloc, and release reservations.
- NOCOW reservation path: `reserve_space()` first tries normal data reservation. On reservation failure, it may call `btrfs_check_nocow_lock()` and reserve metadata only, with cleanup routed through `release_space()` or `shrink_reserved_space()`.
- Extent drop path: `btrfs_drop_extents()` searches file extent items around the requested range, adjusts overlapping regular/prealloc extents, rejects partial inline changes, deletes covered items in batches, updates delayed refs and bytes-found accounting, and may pre-create space for a replacement extent item.
- Fsync path: `btrfs_sync_file()` widens every fsync to the full file range, starts writeback before locking, locks inode plus mmap state, starts writeback again for concurrent dirties, then either waits ordered extents for full sync/zoned filesystems or gathers ordered extents for fast logging. It logs the dentry, syncs the log if possible, or commits the transaction if logging is impossible or fails.
- Mmap write-fault path: `btrfs_page_mkwrite()` reserves data and metadata before folio lock, falls back to metadata-only NOCOW when possible, locks `i_mmap_lock`, locks the folio and io_tree range, waits ordered extents, clips to EOF, marks delalloc, sets dirty/uptodate bits, and returns `VM_FAULT_LOCKED`.
- Hole punching path: `btrfs_fallocate()` routes `FALLOC_FL_PUNCH_HOLE` to `btrfs_punch_hole()`. The punch helper waits ordered extents, zeros unaligned boundary blocks, locks a clean aligned range with `btrfs_punch_hole_lock_range()`, calls `btrfs_replace_file_extents()` with no replacement extent, and updates inode metadata.
- Replacement path: `btrfs_replace_file_extents()` loops over the target range, drops extents, fills holes or clears file-extent tracking, inserts replacement extent items if requested, updates inode time/version at transaction boundaries, restarts transactions, and returns the final open transaction through `trans_out` on success.
- Zero range/fallocate path: `btrfs_zero_range()` avoids work when the target is already preallocated, partially zeros written boundary blocks when needed, reserves data/qgroup space, locks the clean aligned range, then uses `btrfs_prealloc_file_range()` and updates i_size. `btrfs_fallocate()` scans extent maps to build coalesced ranges needing allocation before calling preallocation helpers.
- Seek path: `btrfs_file_llseek()` locks the inode shared and calls `find_desired_extent()`, which locks the searched io_tree range, walks file extent items, treats prealloc and explicit holes as holes, detects implicit holes between extent items, and overlays delalloc/ordered ranges so dirty data is reported as data.

Concurrency and locking:
- Buffered writes take the Btrfs inode lock, using `BTRFS_ILOCK_TRY` for NOWAIT.
- Write preparation locks folios and io_tree ranges and drops those locks to wait ordered extents when conflicts are found.
- NOCOW checks hold `root->snapshot_lock` in write mode while proving and preserving NOCOW eligibility; callers release it with `btrfs_check_nocow_unlock()`.
- Fsync starts writeback outside the inode lock for concurrency, then locks inode plus `i_mmap_lock` to stabilize logging state and starts writeback again to close races.
- `btrfs_page_mkwrite()` uses pagefault accounting, pre-folio-lock reservation, `i_mmap_lock`, folio lock, io_tree extent lock, and ordered-extent waits.
- Hole punching and fallocate take inode and mmap locks exclusively, wait ordered extents, lock aligned io_tree ranges, and assert the target range is clean before metadata mutation.
- `btrfs_punch_hole_lock_range()` repeatedly truncates page cache, locks the io_tree range, and rechecks for folios to avoid racing readers that refault pages.
- Per-file `llseek` cached state is stored in `file->private_data`, guarded by `inode->lock` during installation, and only reused by the owning task.

Important invariants:
- File extent item ranges and file extent presence tracking are sector aligned.
- `btrfs_drop_extents()` does not update VFS inode byte counts itself; it reports `args->bytes_found` so callers can update accounting atomically with extent replacement or removal.
- Partial inline extent replacement/drop is unsupported and returns `-EOPNOTSUPP` in the relevant paths.
- `btrfs_replace_file_extents()` returns an open transaction through `trans_out` on success; callers must update inode metadata as needed and end the transaction.
- Explicit hole items are inserted only when `NO_HOLES` is disabled or replacement logic requires an item; otherwise the file extent presence tree is cleared.
- Fallocate is rejected on zoned filesystems in this path.
- Fast fsync correctness depends on full-file range consideration, ordered extent checksum handling, and hole extent maps; failures to install hole extent maps force full sync.
- `SEEK_HOLE` can return `i_size` quickly only when the inode has no prealloc extents and allocated bytes equal i_size.
- `btrfs_fdatawrite_range()` intentionally performs a second writeback pass for compressed async extents.

Notable risks:
- `btrfs_drop_extents()` and `btrfs_mark_extent_written()` mutate B-tree items, delayed refs, extent-map cache, inode byte accounting, and file extent presence state in tightly coupled sequences; errors often require transaction aborts to avoid corruption.
- Buffered write cleanup has many branches for data reservations, metadata reservations, NOCOW metadata-only state, extent locks, folio references, and cached extent states.
- Mmap write faults reserve before folio locking to avoid deadlocks, so all failure paths must release the correct reservation type and possibly the NOCOW snapshot lock.
- Fsync deliberately widens the requested range; narrowing it would risk missing holes, checksums, or ordered extents documented in the code comments.
- `btrfs_replace_file_extents()` restarts transactions inside a loop, so callers must tolerate partial progress and repeated inode timestamp/version updates.
- Large folio handling in hole punching avoids false positives from generic page-cache range checks; future page-cache changes must preserve the head/tail folio assumptions.
