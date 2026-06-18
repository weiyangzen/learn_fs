# File Research: sources/local-fs/btrfs-linux/fs/btrfs/file.c

## Purpose

Implements the Btrfs regular-file VFS layer: buffered writes, direct/encoded write dispatch, file extent dropping/replacement, prealloc-to-written conversion, fsync/logging, mmap write faults, hole punching, fallocate/zero-range, SEEK_DATA/SEEK_HOLE, file open/read/splice/read/write operations, and writeback kickoff helpers.

## Main Responsibilities

- Marks page-cache folios dirty and updates inode delalloc state.
- Drops, truncates, splits, duplicates, and replaces file extent items.
- Converts preallocated extents to written regular extents, merging adjacent compatible extents when possible.
- Handles buffered write reservations, folio preparation, ordered-extent conflicts, NOCOW fallback, and i_size extension.
- Dispatches encoded, direct, and buffered writes through a shared write entry point.
- Implements fsync using the tree log when possible and full transaction commit when required.
- Handles `page_mkwrite` for writable mmap faults with delalloc/NOCOW accounting.
- Inserts or merges explicit hole extents when `NO_HOLES` is not active.
- Punches holes and replaces ranges with holes or cloned/new extent records.
- Implements fallocate preallocation and zero-range behavior.
- Finds delalloc and ordered extents for correctness of SEEK_DATA/SEEK_HOLE.
- Provides Btrfs regular-file `file_operations`.

## Important APIs And Entry Points

- `btrfs_dirty_folio()` clears stale delalloc accounting, sets delalloc bits, marks folio subranges uptodate/dirty, and extends in-memory `i_size` for writes past EOF.
- `btrfs_drop_extents()` removes or trims file extent items over a range and optionally prepares an insertion slot for replacement.
- `btrfs_mark_extent_written()` turns a prealloc extent range into regular written extents, splitting and merging items as needed.
- `btrfs_check_nocow_lock()` tests whether a buffered write range can use NOCOW and holds the root snapshot lock on success.
- `btrfs_write_check()` performs privilege/time/version updates and expands holes before writes past EOF.
- `btrfs_buffered_write()` is the buffered write loop around `copy_one_range()`.
- `btrfs_do_write_iter()` dispatches encoded, direct, or buffered writes and runs write-sync handling.
- `btrfs_sync_file()` implements file and directory fsync with tree-log fast path and transaction commit fallback.
- `btrfs_replace_file_extents()` drops file extents and inserts holes or replacement extents over a locked range.
- `btrfs_find_delalloc_in_range()` reports contiguous dirty or ordered delalloc subranges.
- `btrfs_fdatawrite_range()` starts writeback, with a second writeback pass when async compression extents are present.

## Extent Mutation Behavior

`btrfs_drop_extents()` is the core file extent removal primitive. It searches `BTRFS_EXTENT_DATA_KEY` items for an inode, handles overlap cases, deletes fully covered items in batches, truncates leading/trailing overlaps, duplicates items for middle-range splits, and updates delayed data refs for real disk extents. It tracks allocated bytes removed through `args->bytes_found` and can insert a replacement item into free leaf space.

`btrfs_mark_extent_written()` requires the target range to be inside a prealloc file extent. It splits the prealloc item into up to three parts, converts the target part to `BTRFS_FILE_EXTENT_REG`, merges with adjacent compatible regular extents using the same disk extent mapping, updates delayed refs, and marks the file extent range as present for safe disk i_size logic.

`fill_holes()` inserts or merges explicit hole file extents when the filesystem does not use `NO_HOLES`. It also installs a hole extent map when possible; if allocation or replacement fails, it drops the extent map range and forces a full inode sync.

`btrfs_replace_file_extents()` is used by hole punching and extent replacement. It starts bounded transactions with a temp block reserve, loops over the range, drops existing extents, fills explicit holes or clears file-extent tracking beyond EOF, inserts replacement extents when supplied, updates inode version/times, periodically ends transactions, and returns the final transaction handle on success.

## Write Path

Buffered writes run under the Btrfs inode lock. `copy_one_range()` faults user pages, reserves data and metadata space, optionally falls back to NOCOW metadata-only reservation, prepares a locked folio, waits out overlapping ordered extents, copies into the folio, shrinks unused reservations after short copies, calls `btrfs_dirty_folio()`, unlocks extents and folios, and releases reservation state.

`reserve_space()` first tries normal data reservation. If that fails and the range can be NOCOW, it reserves metadata only and leaves the snapshot lock held until release. NOWAIT writes return `-EAGAIN` when they would need blocking reservation or COW work.

`btrfs_do_write_iter()` rejects writes after shutdown or filesystem error, disallows NOWAIT encoded writes, dispatches encoded/direct/buffered paths, records the inode's last subtransaction, and applies `generic_write_sync()` for synchronous writes.

## Fsync And Logging

`btrfs_sync_file()` always expands the requested fsync range to the full file to avoid missing holes, file extent items, or checksums. It starts writeback before and after taking inode/mmap locks, decides whether a full sync is required, waits for ordered extents for full sync or zoned filesystems, otherwise captures ordered extents for fast logging and waits for writeback.

If logging can be skipped because the inode is already logged or committed, it clears stale full-sync state and checks writeback errors. Otherwise it starts a transaction, logs the dentry, syncs the log when possible, or falls back to committing the transaction. For fast fsync fallback it ends the transaction, waits for ordered extents, attaches to the transaction barrier, and commits only what is necessary.

## Mmap, Hole Punch, And Fallocate

`btrfs_page_mkwrite()` reserves delalloc space before locking the faulting folio to avoid dirty-page deadlocks, handles NOCOW metadata-only fallback, locks the mmap and extent ranges, waits for ordered extents, trims reservation at EOF, sets delalloc and folio dirty/uptodate state, zeroes bytes past EOF, and returns the folio locked to the VM.

`btrfs_punch_hole()` handles unaligned boundaries by zeroing partial sectors with `btrfs_truncate_block()`, skips already-hole ranges, flushes ordered extents, locks and truncates page cache over aligned ranges, calls `btrfs_replace_file_extents()` with no replacement extent, and updates inode metadata.

`btrfs_fallocate()` rejects unsupported modes and zoned filesystems, handles punch-hole and zero-range modes, expands preceding holes if needed, waits for ordered extents, reserves qgroup/data space for real holes, preallocates missing ranges, and updates i_size unless `FALLOC_FL_KEEP_SIZE` is set.

`btrfs_zero_range()` avoids work if the range is already preallocated, zeroes written unaligned boundaries, includes hole boundary sectors in allocation, reserves data/qgroup space, and uses preallocation to represent the zero range.

## SEEK_DATA/SEEK_HOLE

`find_desired_extent()` locks the target inode range and scans file extent items with forward readahead. It treats explicit holes, implicit `NO_HOLES` gaps, and prealloc extents as holes, but overlays delalloc and ordered extents so dirty data is reported as data before it has landed in the btree. It caches llseek extent-state lookup state per file/private owner task for repeated seeks.

## File Operations

`btrfs_file_operations` wires Btrfs regular files to llseek, read_iter, splice_read, write_iter, splice_write, mmap_prepare, open, release, fsync, fallocate, ioctls, remap_file_range, uring commands, NOWAIT/direct capability, buffered async flags, and generic leases.

## Dependencies

This file integrates with extent maps, ordered extents, delayed refs, transactions, tree logging, delalloc space accounting, qgroups, direct IO, encoded IO, compression writeback, reflink/remap, subpage folio state, inode runtime flags, mmap locks, VFS writeback/error handling, fsverity open checks, and Btrfs block reserves.

## Invariants And Risks

- Extent mutation requires strict inode, extent-range, path, and transaction locking; wrong ordering can corrupt file extent items or delayed refs.
- `btrfs_drop_extents()` must update extent refs for real disk extents but not for holes or log-tree-only operations.
- NOCOW success leaves the snapshot lock held and callers must release it through `btrfs_check_nocow_unlock()`.
- Fsync correctness depends on flushing the full file range and coordinating ordered extents with log-tree checksum/file extent logging.
- `page_mkwrite()` must reserve before folio locking and must recheck EOF/truncation after locks are acquired.
- Hole punching must remove page cache and wait for ordered extents before replacing file extent items.
- SEEK_DATA/HOLE must combine btree extents with delalloc and ordered extents to avoid reporting dirty data as a hole.
