# `sources/user-network-fs/go-fuse/internal/renameat/renameat_freebsd.go`

## Purpose
FreeBSD renameat implementation.

## Important APIs, Types, And Functions
Defines Linux-compatible `RENAME_EXCHANGE` constant but returns ENOSYS for nonzero flags; plain rename delegates to `unix.Renameat`.

## Control Flow
Defines Linux-compatible `RENAME_EXCHANGE` constant but returns ENOSYS for nonzero flags; plain rename delegates to `unix.Renameat`.

## State And Persistence
Persistent namespace change only. Risk is callers expecting exchange/no-replace semantics on FreeBSD.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Persistent namespace change only. Risk is callers expecting exchange/no-replace semantics on FreeBSD.

## Test Signals
Persistent namespace change only. Risk is callers expecting exchange/no-replace semantics on FreeBSD.
