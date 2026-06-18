# `sources/user-network-fs/go-fuse/internal/openat/openat_linux.go`

## Purpose
Linux no-symlink open implementation.

## Important APIs, Types, And Functions
Uses `openat2` with `RESOLVE_NO_SYMLINKS`, `O_CLOEXEC`, and falls back to `openat` with `O_NOFOLLOW` on ENOSYS.

## Control Flow
Uses `openat2` with `RESOLVE_NO_SYMLINKS`, `O_CLOEXEC`, and falls back to `openat` with `O_NOFOLLOW` on ENOSYS.

## State And Persistence
Transient fd state only. Risk is weaker fallback on old kernels and correct mode/flags propagation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Transient fd state only. Risk is weaker fallback on old kernels and correct mode/flags propagation.

## Test Signals
Transient fd state only. Risk is weaker fallback on old kernels and correct mode/flags propagation.
