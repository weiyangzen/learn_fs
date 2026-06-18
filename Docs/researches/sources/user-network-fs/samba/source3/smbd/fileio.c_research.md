# sources/user-network-fs/samba/source3/smbd/fileio.c

## Purpose
`fileio.c` provides core synchronous read, write, modification bookkeeping, write-time update, and fsync helpers for `files_struct` objects.

## Important APIs, types, and functions
- `read_file()` validates range, rejects print files, calls `SMB_VFS_PREAD()`, and updates fd-handle position and SMB position information.
- `write_file()` routes print spool writes, checks write capability, contends level2 oplocks, preserves sticky write times, calls `real_write_file()`, and marks files modified.
- `real_write_file()` validates write ranges, optionally fills sparse gaps under strict allocation, and calls `vfs_pwrite_data()`.
- `trigger_write_time_update_immediate()` updates mtime or forces a ctime change unless POSIX open or sticky write time blocks it.
- `prepare_file_modified()` and `mark_file_modified()` restore forced write times, set modified flags, and set archive attributes after writes.
- `sync_file()` conditionally calls `smb_vfs_fsync_sync()` for strict sync/write-through requests.

## Control flow
Reads and writes both validate VFS ranges and update `fh->pos`. Writes to print files bypass filesystem write and call `print_spool_write()`. Normal writes check `fsp_flags.can_write`, trigger level2 oplock contention, snapshot mtime if write time is forced, perform the pwrite, then mark the FSP modified. Modification bookkeeping restores sticky mtime by calling `smb_set_file_time()` if needed, sets `fsp_flags.modified` once, and sets the archive bit through DOS mode code when configured and not already set.

## State and persistence behavior
Persistent state changes include file data writes, optional sparse preallocation/fill, timestamp changes, archive attribute changes, print spool writes, and fsync. In-memory state includes fd-handle position, position information after reads, `fsp_flags.modified`, and cached stat timestamps updated through lower layers.

## Dependencies and integration points
It depends on VFS pread/pwrite/fsync/range helpers, print spool APIs, oplock contention, DOS mode/attribute setting, timestamp setting, fd-handle accessors, and share options such as strict allocate, store DOS attributes, map archive, strict sync, and sync always.

## Risks and edge cases
- Writes intentionally do not update SMB position information, matching Samba test expectations.
- Sticky write time restoration temporarily clears cached mtime to force lower layers to set the requested time.
- Strict allocation can fail before write if sparse gap filling fails.
- `sync_file()` returns invalid handle for fd `-1`; pathref and fake/print routes must avoid inappropriate sync.
- Archive-bit updates after write can introduce extra metadata failures/notifications.

## Test signals
Tests should cover range validation, read position updates, write position but not position-information behavior, print file writes, permission denial, strict allocation failure, sticky write-time restoration, archive bit setting, modified close notification behavior, immediate mtime/ctime updates, and strict sync/write-through combinations.
