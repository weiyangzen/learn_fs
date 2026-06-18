# sources/storage-engines/badger/y/file_dsync.go

## Purpose
This platform-specific file sets the datasync open flag for platforms that support `O_DSYNC`.

## Important APIs, Types, And Functions
The `init` function assigns `datasyncFileFlag = unix.O_DSYNC`. Build tags exclude DragonFly, FreeBSD, Windows, Plan 9, JS, and WASI.

## Control Flow
At package initialization, the platform constant is copied into the shared variable used by file-opening helpers in `y.go`.

## State And Persistence Behavior
This affects persistence semantics of files opened with the `Sync` flag or `sync=true`, causing writes to wait for data sync on supported Unix-like systems.

## Dependencies And Integration Points
It depends on `golang.org/x/sys/unix` and integrates with `OpenExistingFile`, `CreateSyncedFile`, `OpenSyncedFile`, and `OpenTruncFile`.

## Risks And Edge Cases
Build tag coverage controls which synchronization semantics are used. Incorrect tags would silently choose the wrong flag file.

## Test Signals
There is no direct test. Persistence behavior is indirectly exercised by Badger write/recovery tests.
