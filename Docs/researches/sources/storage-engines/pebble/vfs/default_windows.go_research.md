# Research: sources/storage-engines/pebble/vfs/default_windows.go

## Purpose
`vfs/default_windows.go` provides Windows-specific wrappers for Pebble's default VFS files and directories.

## Important APIs, Types, And Functions
`wrapOSFileImpl` returns `windowsFile`. `defaultFS.OpenDir` opens a path with `O_CLOEXEC` and returns `windowsDir`. `windowsDir` implements `Stat`, no-op prefetch/preallocate, no-op `Sync`, no-op `SyncData`, and no-op `SyncTo`. `windowsFile` implements no-op prefetch/preallocate, `Stat`, `SyncData` as `Sync`, and `SyncTo` as full `Sync`. `deviceIDFromFileInfo` returns an empty `DeviceID` because it is unsupported.

## Control Flow
File operations delegate to `os.File`, except unsupported advisory operations are no-ops. Directory syncs are intentionally ignored to match RocksDB Windows behavior. File `SyncTo` performs a full sync and reports `fullSync=true`.

## State And Persistence
The wrapper introduces no additional state. File durability depends on Windows file sync semantics. Directory durability is not explicitly enforced through `Sync`.

## Dependencies And Integration Points
It depends on Windows build tags, `os`, `syscall`, Cockroach errors, and the Pebble `vfs.File` interface. It provides compatibility for code paths that assume directory objects implement sync-related methods.

## Risks And Edge Cases
Ignoring directory sync means crash-safety semantics differ from Unix. `deviceIDFromFileInfo` cannot distinguish devices, so disk-health or placement logic depending on IDs must tolerate an empty ID. Prefetch and preallocation are not implemented.

## Test Signals
Signals include Windows interface conformance, file sync behavior through `SyncData`/`SyncTo`, directory sync no-op behavior, unsupported device ID handling, and no-op prefetch/preallocate calls.
