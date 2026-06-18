# sources/sync-backup/casync/src/copy.c

## Purpose

`copy.c` implements `copy_bytes()`, an optimized fd-to-fd byte copier that tries in-kernel copy mechanisms first and falls back to buffered read/write. It supports copying until EOF or a caller-specified byte limit.

## Important APIs, Types, and Functions

When libc/kernel headers lack `copy_file_range()`, the file defines syscall numbers for common architectures and provides a local wrapper. `try_copy_file_range()` caches whether the syscall exists using a static `have` flag and returns negative errno-style results. `copy_bytes(int fdf, int fdt, uint64_t max_bytes)` tries `copy_file_range`, then `sendfile`, then `splice`, then manual read and `loop_write()`.

## Control Flow

The copy loop maintains `m`, the maximum per-call copy size, capped by `max_bytes` when finite. Unsupported or unsuitable errors from each optimized mechanism disable only that mechanism and fall through to the next option. A zero-byte result from a mechanism means EOF and terminates. After each successful copy, finite `max_bytes` is decremented; when it reaches zero the function returns `1`. EOF before the limit returns `0`.

## State and Persistence Behavior

The only process state is `try_copy_file_range()`'s static availability cache. Persistent effects are bytes written to the target fd and advancement of the fds' current offsets. No explicit fsync is performed.

## Dependencies and Integration Points

The file includes `copy.h`, uses `BUFFER_SIZE` from shared headers, and relies on utility helpers/macros such as `IN_SET`, `MIN`, `MAX`, and `loop_write()`. It likely supports decoder extraction or store/archive file copying.

## Risks and Edge Cases

The manual fallback declares `uint8_t buf[MIN(m, BUFFER_SIZE)]`; very large or dynamic stack allocation behavior depends on compiler support for VLAs and `m` staying bounded. The final update `m = MAX(MIN(BUFFER_SIZE, max_bytes), m - n)` behaves oddly when `max_bytes == (uint64_t)-1`, because `MIN(BUFFER_SIZE, max_bytes)` is still `BUFFER_SIZE`, but this mainly keeps a lower bound. Kernel copy operations may fail with filesystem-specific errors and fall back only for selected errno values. `splice()` between arbitrary fds may not be valid.

## Test Signals

Tests should copy regular files with exact limit, EOF before limit, unlimited copy, zero limit, pipes where `sendfile` or `splice` behavior differs, forced `copy_file_range` `ENOSYS` fallback, cross-filesystem `EXDEV`, and short writes in `loop_write()` using a pipe or fault-injection wrapper.
