# sources/test-tools/fio/os/os.h

## Purpose
`os.h` is fio's cross-platform OS abstraction umbrella. It selects the platform-specific header, fills missing feature defaults, provides generic fallbacks, normalizes byte-order helpers, and exposes common helpers for cache line size, block sizing, random seed initialization, filesystem free space, CPU count, thread id, shared-memory behavior, fallocate, CPU feature probing, mkdir, and clock ticks.

## Important APIs, Types, and Functions
It defines OS enum IDs, `cpu_features`, includes the selected `os-*.h`, and supplies fallback macros for `EDQUOT`, `OS_MSG_DONTWAIT`, POSIX fadvise constants, CPU affinity, I/O priority, `OS_O_DIRECT`, huge pages, `FIO_O_NOATIME`, `OS_RAND_MAX`, preferred engine/clock/path separator, `socklen_t`, `os_ctime_r`, byte swapping, endian conversion, `os_cache_line_size()`, generic `blockdev_size()`, generic `init_random_seeds()`, `get_fs_free_size()`, `cpus_configured()`, `CPU_COUNT()`, `gettid()`, `shm_attach_to_open_removed()`, `fio_fallocate()`, `os_cpu_has()`, `fio_mkdir`, and `os_clk_tck()`.

## Control Flow
Preprocessor OS detection includes exactly one platform header or errors out. Runtime helpers are mostly simple fallbacks: read `/dev/urandom`, seek to file end for generic block size, query `sysconf()`, count CPU bits by iterating configured CPUs, or return safe unsupported defaults. Endian macros use platform byte-swap functions or generic swaps depending on configuration.

## State and Persistence
The header owns no state. Generic helpers may read random bytes or seek an fd; fallback `fio_fallocate()` sets `errno = ENOSYS`.

## Dependencies and Integration Points
Nearly all fio source includes this abstraction directly or indirectly. It is the contract that allows `options.c`, engines, file code, memory allocators, logging, verification, and platform-specific code to compile against common names.

## Risks and Edge Cases
Fallbacks often return success/no-op for unsupported features, so compile-time feature macros must be correct to avoid silently ignoring user intent. Generic `blockdev_size()` changes the fd offset with `lseek()`. Endian typecheck macros require correct integer widths. `os_clk_tck()` is external on platforms lacking `_SC_CLK_TCK`, requiring platform implementation.

## Test Signals
Builds on every supported OS, feature-matrix tests for unsupported options, endian conversion unit tests, random seed fallback tests, generic block size tests, CPU count and affinity fallback tests, and clock tick link tests are useful.
