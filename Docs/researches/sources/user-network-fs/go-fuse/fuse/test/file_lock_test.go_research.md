# `sources/user-network-fs/go-fuse/fuse/test/file_lock_test.go`

## Purpose
Linux integration tests for flock/lock dispatch.

## Important APIs, Types, And Functions
Defines `TestFlockExclusive`, `lockingNode`, `TestFlockInvoked`, and `TestNoLockSupport`.

## Control Flow
Defines `TestFlockExclusive`, `lockingNode`, `TestFlockInvoked`, and `TestNoLockSupport`.

## State And Persistence
State includes OS advisory locks and invocation booleans guarded by mutex. It validates `EnableLocks`, file lock handlers, and VFS fallback when fs returns ENOSYS. Risks include external `flock` availability and platform lock semantics.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State includes OS advisory locks and invocation booleans guarded by mutex. It validates `EnableLocks`, file lock handlers, and VFS fallback when fs returns ENOSYS. Risks include external `flock` availability and platform lock semantics.

## Test Signals
State includes OS advisory locks and invocation booleans guarded by mutex. It validates `EnableLocks`, file lock handlers, and VFS fallback when fs returns ENOSYS. Risks include external `flock` availability and platform lock semantics.
