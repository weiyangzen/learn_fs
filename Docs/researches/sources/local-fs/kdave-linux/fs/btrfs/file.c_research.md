# File Research: sources/local-fs/kdave-linux/fs/btrfs/file.c

Btrfs VFS regular-file operations and file extent mutation implementation. This file handles buffered writes, direct/encoded write dispatch, page-cache dirtying, fsync, mmap write faults, extent dropping/replacement, hole punching, fallocate, zero range, SEEK_DATA/SEEK_HOLE, open/read/splice dispatch, and the exported file operations table.

Key responsibilities:
- Implements page-cache dirtying for buffered writes through `btrfs_dirty_folio()`, including delalloc state, uptodate/dirty folio bits, and in-memory i_size extension.
- Drops and rewrites file extent items with `btrfs_drop_extents()`, handling full deletion, truncation, splitting, inline extent rejection, reference count updates, extent-map cache drops, and optional replacement item setup.
- Converts preallocated extents to written extents through `btrfs_mark_extent_written()`, including splitting, merging with adjacent compatible extents, delayed ref updates, and file extent range tracking.
- Prepares folios for writes, reads partial blocks when needed, locks ranges, waits for ordered extents, and retries when folios are invalidated.
- Checks NOCOW write eligibility with snapshot serialization, ordered-range flushing, and `can_nocow_extent()` probing.
- Performs generic write validation, privilege stripping, ctime/mtime/i_version updates, and pre-write hole expansion in `btrfs_write_check()`.
- Reserves and releases data/metadata space for buffered writes, including NOCOW metadata-only reservations and NOWAIT behavior.
- Implements the buffered write loop by copying one folio-sized range at a time, shrinking reservations on short copies, marking delalloc, and updating `ki_pos`.
- Dispatches encoded, direct, and buffered writes from `btrfs_do_write_iter()` and performs post-write sync handling.
- Releases per-file private state and flush-on-close state in `btrfs_release_file()`.
- Implements `btrfs_sync_file()` with ordered writeback, inode/mmap locking, fast vs full fsync decisions, log-tree logging, log sync, and transaction commit fallback.
- Implements mmap `page_mkwrite`, including delalloc reservation before folio lock, EOF/truncate races, ordered extent waits, partial EOF zeroing, and subpage/folio dirty state.
- Creates or merges explicit hole extents for non-`NO_HOLES` filesystems and updates extent maps for fsync correctness.
- Replaces file extents for hole punching, clone/dedupe-style replacement, and preallocation workflows with transaction restart handling.
- Implements `btrfs_punch_hole()`, including unaligned head/tail zeroing, ordered extent waits, range locking, file extent replacement, inode timestamp/version updates, and transaction completion.
- Implements fallocate and zero-range behavior, including qgroup/data reservations, preallocation range coalescing, zoned rejection, keep-size handling, and i_size updates.
- Finds delalloc/ordered subranges and uses them to implement correct `SEEK_DATA` and `SEEK_HOLE` behavior over explicit extents, implicit holes, prealloc extents, and dirty ranges.
- Defines `btrfs_file_operations` and read/open/splice/mmap/llseek dispatch.
- Provides `btrfs_fdatawrite_range()`, with a second writeback pass for compressed async extents.

Important data flows:
- Buffered write path: `btrfs_file_write_iter()` calls `btrfs_do_write_iter()`, which selects `btrfs_buffered_write()` unless direct or encoded I/O is requested. The buffered loop validates via `generic_write_checks()` and `btrfs_write_check()`, then repeatedly calls `copy_one_range()` to reserve space, prepare a folio, lock/wait extents, copy user data, dirty delalloc state, and release reservations.
- Fsync path: `btrfs_sync_file()` writes dirty ranges, locks inode and mmap state, starts more writeback for races, waits for ordered extents or writeback depending on full/fast sync, logs the dentry into the tree log, syncs the log when possible, otherwise falls back to transaction commit.
- Hole punching path: `btrfs_fallocate()` routes `FALLOC_FL_PUNCH_HOLE` to `btrfs_punch_hole()`, which handles unaligned zeroing, locks a clean aligned range with `btrfs_punch_hole_lock_range()`, then calls `btrfs_replace_file_extents()` without replacement extent info to drop extents and insert hole representation where required.
- Replacement path: `btrfs_replace_file_extents()` starts a transaction with temporary metadata reserve, repeatedly calls `btrfs_drop_extents()`, fills holes or clears file extent presence state, optionally inserts replacement extent items with `btrfs_insert_replace_extent()`, updates inode metadata, ends/restarts transactions, and returns the final open transaction through `trans_out`.
- SEEK_DATA/SEEK_HOLE path: `btrfs_file_llseek()` locks the inode shared, then `find_desired_extent()` locks the searched io_tree range, walks file extent items, and consults `btrfs_find_delalloc_in_range()` so dirty delalloc and ordered extents are reported as data even before file extent items exist.

Concurrency and locking:
- Buffered writes take the Btrfs inode lock, optionally with `BTRFS_ILOCK_TRY` for NOWAIT.
- File extent replacement and hole punching require inode and mmap locks plus aligned io_tree range locks after ordered extents are flushed.
- `btrfs_check_nocow_lock()` takes the root snapshot lock as a write lock while determining and preserving a NOCOW-writeable range; callers must release it with `btrfs_check_nocow_unlock()`.
- `btrfs_page_mkwrite()` uses `sb_start_pagefault()`, `i_mmap_lock`, folio lock, and io_tree extent locks while avoiding delalloc reservation under the folio lock.
- `btrfs_sync_file()` deliberately starts writeback before taking the inode lock, then repeats after locking to close races with concurrent dirtying.
- Per-file llseek cached state is stored in `file->private_data` and guarded by `inode->lock`; cached delalloc state is only reused by its owner task.

Important invariants:
- Extent item ranges and file extent presence tracking are sector aligned.
- `btrfs_drop_extents()` does not update VFS inode byte counts itself; callers use `args->bytes_found` to update accounting atomically with replacement/drop operations.
- Inline extents cannot be partially split for drop/replace operations and return `-EOPNOTSUPP` in those cases.
- `btrfs_replace_file_extents()` returns an open transaction through `trans_out` on success; callers are responsible for final inode updates and ending the transaction.
- Hole extent items are inserted only when `NO_HOLES` is not enabled or when replacement requires an explicit item; otherwise file extent presence tracking is cleared.
- Fallocate is rejected on zoned filesystems in this path.
- Fast fsync correctness depends on extent maps for holes and on ordered extent checksum availability, so extent-map update failures force full sync.
- `SEEK_HOLE` can return i_size quickly only when there are no prealloc extents and inode bytes equal i_size.

Notable risks:
- `btrfs_drop_extents()` and `btrfs_mark_extent_written()` mutate B-tree items, references, and extent-map/file-extent range state in tightly coupled steps; transaction aborts are used when invariants fail.
- Buffered write reservation has multiple cleanup branches for data reservation, metadata reservation, NOCOW metadata-only reservation, extent locks, folio references, and cached states; future changes must preserve balanced release paths.
- mmap write faults reserve space before folio locking to avoid deadlock with writeback, so error handling must carefully release either data+metadata or metadata-only NOCOW reservations.
- Fsync intentionally widens all ranges to the whole file to avoid missing holes, checksums, or ordered extents; narrowing it would require revalidating several documented corruption races.
- `btrfs_replace_file_extents()` restarts transactions inside a loop, so callers must tolerate partial progress and updated inode timestamps/version between transaction boundaries.
