<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_write.go -->
# sources/user-network-fs/rclone/vfs/read_write.go

## Purpose
Implements `RWFileHandle`, the cache-backed file handle for read/write, write-only with cache, and cache-mode read paths. It uses `vfscache.Item` as the local backing file and schedules writeback on close.

## Important APIs, Types, and Functions
Key APIs are `RWFileHandle`, `newRWFileHandle`, `readOnly`, `writeOnly`, `openPending`, `Read`, `ReadAt`, `Seek`, `Write`, `WriteAt`, `WriteString`, `Truncate`, `Sync`, `Flush`, `Release`, `Close`, `Size`, `Stat`, and unsupported OS-file methods.

## Control Flow
Construction obtains a cache item, determines existence from `File` or unwritten cache state, enforces `O_CREATE|O_EXCL`, truncates immediately for `O_TRUNC` or new create, marks dirty when needed, and registers a writer for non-read-only handles. `openPending` serializes with `File.muRW`, opens the cache item against the current object, sets append or start offset, marks opened, and inserts the object into the directory cache. Reads and writes check closed/access mode, open lazily, then delegate to `Item.ReadAt`/`WriteAt`; writes update size and append offsets. Close updates file size, closes the item with `file.setObject`, applies pending modtime for unopened handles, and deregisters writers.

## State and Persistence Behavior
Persistent writes are local until `Item.Close` and writeback upload. `File.size`, writer count, dirty state, pending modtimes, and directory virtual entries are updated during handle lifetime. `Sync` flushes the local cache item, not necessarily remote upload completion. Close errors intentionally leave cache files around for recovery.

## Dependencies and Integration Points
Depends on `vfscache.Item`, `File` writer tracking, `Dir.addObject`, VFS cache options, and writeback behavior hidden behind `Item.Close`. It is selected by `File.Open` for cache modes and many read/write flag combinations.

## Risks and Edge Cases
`Fd` returns a placeholder `0xdeadbeef`. Locking deliberately releases `fh.mu` around `ReadAt`/`WriteAt` I/O when requested, which requires careful state consistency. `O_SYNC` is not a real remote sync. Unopened handles can close without opening and only apply pending modtime. Append mode modifies `WriteAt` semantics by writing at EOF, matching POSIX append but surprising for positional writes.

## Test Signals
`read_write_test.go` covers method behavior, seeks, read/write/read-at/write-at, truncation, size updates, open flag matrix for writes/full cache modes, modtime with open writers, cache rename, and external update refresh.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_write.go -->
