# `sources/user-network-fs/go-fuse/internal/renameat/renameat_linux.go`

## Purpose
Linux renameat implementation.

## Important APIs, Types, And Functions
Defines `RENAME_EXCHANGE` from `unix` and delegates to `unix.Renameat2`.

## Control Flow
Defines `RENAME_EXCHANGE` from `unix` and delegates to `unix.Renameat2`.

## State And Persistence
Persistent namespace change only. Risk is kernel/filesystem support for flags and errno propagation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Persistent namespace change only. Risk is kernel/filesystem support for flags and errno propagation.

## Test Signals
Persistent namespace change only. Risk is kernel/filesystem support for flags and errno propagation.
