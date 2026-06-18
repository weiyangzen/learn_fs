# Research: sources/storage-engines/pebble/vfs/default_linux.go

## Purpose
`vfs/default_linux.go` provides Linux-specific wrappers around `os.File` for Pebble's default VFS. It implements Linux prefetch, preallocation, fdatasync, partial sync hints, directory opening, and device ID extraction.

## Important APIs, Types, And Functions
`wrapOSFileImpl` returns a `linuxFile` and detects whether `sync_file_range` is supported for the file descriptor. `defaultFS.OpenDir` opens a directory with `O_CLOEXEC` and returns `linuxDir`. `linuxFile` implements `Prefetch` via `readahead`, `Preallocate` via `fallocate`, `SyncData` via `fdatasync`, and `SyncTo` via either `fdatasync` or `sync_file_range`. `isSyncRangeSupported` allowlists ext filesystems and calls `syncRangeSmokeTest`. `deviceIDFromFileInfo` extracts major/minor device numbers from `syscall.Stat_t`.

## Control Flow
On file wrap, the code records the fd and checks filesystem support. `SyncTo` falls back to full `fdatasync` when sync range is unsupported, otherwise issues asynchronous writeback for `[0, offset]` with wait-before semantics. Directory methods mostly delegate to `os.File` and make unsupported file operations no-ops.

## State And Persistence
The wrapper persists data through kernel sync syscalls. `useSyncRange` is per-file transient state based on filesystem type and syscall availability. Directory `SyncData` delegates to full sync.

## Dependencies And Integration Points
It depends on Linux build tags, `golang.org/x/sys/unix`, syscall constants, Pebble `File` interface expectations, and default FS wrapping in other VFS files. Pebble write paths use these methods for durability and writeback throttling.

## Risks And Edge Cases
`sync_file_range` does not provide persistence guarantees, so `SyncTo` reports `fullSync=false`. The allowlist avoids filesystems where it may be a noop, but only ext filesystems are enabled. WSL ENOSYS disables it. Offset/length conversion in readahead uses uintptr and assumes valid nonnegative inputs from callers.

## Test Signals
Tests should cover interface conformance, fdatasync fallback, sync range smoke-test behavior, filesystem allowlist decisions, directory open/sync behavior, and device ID extraction on Linux.
