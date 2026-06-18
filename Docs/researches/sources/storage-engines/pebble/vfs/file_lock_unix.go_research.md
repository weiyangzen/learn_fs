<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_unix.go -->
# sources/storage-engines/pebble/vfs/file_lock_unix.go

## Purpose
Implements `vfs.Default.Lock` on Unix-like platforms using advisory `fcntl` write locks plus process-local duplicate-lock tracking.

## Important APIs, Types, and Functions
`lockedFiles` is a global map protected by a mutex. `lockCloser` wraps the lock file and releases the map entry on close. `defaultFS.Lock` creates/truncates the file, attempts `unix.FcntlFlock` with `F_SETLK`, and returns a closer.

## Control Flow
`Lock` first rejects paths already locked by this process. It creates the lock file, constructs a whole-file write lock, and attempts a non-blocking `F_SETLK`. On OS lock failure it closes the file and returns the errno. On success it records the name in `lockedFiles` and returns a `lockCloser`. `Close` checks the map, deletes the entry, and closes the file, releasing the advisory lock.

## State and Persistence Behavior
The lock file is created/truncated and remains on disk. Lock state is partly OS-managed and partly tracked in the process-local map to avoid fcntl's same-process semantics accidentally replacing/releasing locks.

## Dependencies and Integration Points
Used by `vfs.Default.Lock` and tested by `file_lock_test.go`. Pebble uses this to coordinate DB ownership across processes.

## Risks and Edge Cases
Unix advisory locks can be released by closing another descriptor for the same file, which the interface comment warns about. Path keys are raw strings, so aliases/symlinks may bypass the same-process map. `Close` panics if called on a lock not marked held.

## Test Signals
`file_lock_test.go` verifies subprocess exclusion, release, and duplicate same-process detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_unix.go -->
