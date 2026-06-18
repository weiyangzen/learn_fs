# `sources/user-network-fs/go-fuse/internal/openat/openat_unix.go`

## Purpose
Non-Linux no-symlink open fallback.

## Important APIs, Types, And Functions
Uses `unix.Openat` with `O_NOFOLLOW|O_CLOEXEC`.

## Control Flow
Uses `unix.Openat` with `O_NOFOLLOW|O_CLOEXEC`.

## State And Persistence
No persistence. Risk is explicitly documented: `O_NOFOLLOW` protects only the final component, not intermediate symlinks.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Risk is explicitly documented: `O_NOFOLLOW` protects only the final component, not intermediate symlinks.

## Test Signals
No persistence. Risk is explicitly documented: `O_NOFOLLOW` protects only the final component, not intermediate symlinks.
