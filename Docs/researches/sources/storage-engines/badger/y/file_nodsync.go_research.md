# sources/storage-engines/badger/y/file_nodsync.go

## Purpose
This platform-specific file provides a fallback synchronization flag for platforms without `O_DSYNC`.

## Important APIs, Types, And Functions
The `init` function sets `datasyncFileFlag = syscall.O_SYNC` under build tags for DragonFly, FreeBSD, Windows, and Plan 9.

## Control Flow
The assignment happens at package initialization before file helper functions are used.

## State And Persistence Behavior
Files opened with sync semantics use full `O_SYNC` rather than datasync-only behavior on these platforms, potentially increasing durability cost.

## Dependencies And Integration Points
It depends on the standard `syscall` package and the shared helpers in `y.go`.

## Risks And Edge Cases
The build tags do not include JS/WASI, which are excluded from the dsync file but not included here; those platforms may be unsupported or handled elsewhere by build constraints.

## Test Signals
No direct test exists. Platform CI/build coverage is the main signal.
