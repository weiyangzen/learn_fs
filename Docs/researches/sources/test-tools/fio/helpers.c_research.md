# sources/test-tools/fio/helpers.c

## Purpose
Provides portability stubs for optional platform syscalls that fio can call even when the host libc or OS lacks support.

## Important APIs, Types, and Functions
Conditionally defines `fallocate`, `posix_fallocate`, `sync_file_range`, `syncfs`, and `posix_fadvise` when the corresponding `CONFIG_*` feature macro is absent.

## Control Flow
Unsupported operations either set `errno = ENOSYS` and return `-1` (`fallocate`, `sync_file_range`, `syncfs`) or become successful no-ops (`posix_fallocate`, `posix_fadvise`) depending on fio's expected fallback behavior.

## State and Persistence Behavior
No state is persisted. The only side effect is setting `errno` for explicit unsupported errors.

## Dependencies and Integration Points
Includes `helpers.h` and `errno.h`. Used by file setup, cache advice, allocation, and sync paths so call sites can compile across platforms without sprinkling feature guards everywhere.

## Risks
No-op `posix_fallocate()` and `posix_fadvise()` can make a build appear to support behavior that the OS does not actually perform. Callers must treat these as compatibility shims rather than guarantees of preallocation or advisory cache behavior.

## Test Signals
Build matrix coverage with feature macros enabled and disabled is most important. Runtime tests should verify unsupported sync/allocation operations surface `ENOSYS` where callers expect fallback behavior.
