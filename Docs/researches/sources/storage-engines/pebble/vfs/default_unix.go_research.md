# Research: sources/storage-engines/pebble/vfs/default_unix.go

## Purpose
`vfs/default_unix.go` implements default VFS file wrappers for non-Linux Unix platforms: Darwin, DragonFly, FreeBSD, NetBSD, OpenBSD, and Solaris.

## Important APIs, Types, And Functions
`wrapOSFileImpl` returns a `unixFile` with the underlying `os.File` and fd. `defaultFS.OpenDir` opens a directory with `O_CLOEXEC`. `unixFile` implements `Stat`, no-op `Prefetch` and `Preallocate`, `SyncData` as full `Sync`, and `SyncTo` as full `Sync` returning `fullSync=true`. `deviceIDFromFileInfo` extracts major/minor device numbers through `unix.Major` and `unix.Minor`.

## Control Flow
All file operations mostly delegate to the embedded `os.File`. Since these platforms do not use Linux `sync_file_range` here, any `SyncTo` request becomes a full sync.

## State And Persistence
No extra persistent state is introduced. Durability relies on the platform's `fsync` behavior through `os.File.Sync`. Directory files are wrapped in the same `unixFile` type.

## Dependencies And Integration Points
It depends on build tags, `golang.org/x/sys/unix`, `syscall.Stat_t`, and the Pebble `vfs.File` interface. It provides the platform-specific layer below default FS consumers.

## Risks And Edge Cases
Prefetch and preallocation are silent no-ops, so performance and space-reservation behavior differs from Linux. `SyncTo` is conservative but potentially more expensive because it performs a full sync. `OpenDir` passes `O_CLOEXEC` with read mode zero; platform differences in opening directories matter.

## Test Signals
Useful signals include interface conformance, successful directory opening/syncing, device ID extraction, no-op prefetch/preallocate behavior, and full-sync behavior for `SyncData` and `SyncTo`.
