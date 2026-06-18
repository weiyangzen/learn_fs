# sources/test-tools/fio/os/os-qnx.h

## Purpose
`os-qnx.h` adapts fio to QNX. It provides missing POSIX/Linux-like definitions, disables SysV shared-memory header use, and implements block sizing, memory sizing, filesystem free-space, thread id feature declaration, and byte swaps.

## Important APIs, Types, and Functions
It defines `FIO_OS os_qnx`, `FIO_NO_HAVE_SHM_H`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_FS_STAT`, `FIO_HAVE_GETTID`, local `__u64`/`__u32`, `SA_RESTART` fallback, `OS_MAP_ANON`, and helpers `blockdev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, and `get_fs_free_size()`.

## Control Flow
`blockdev_size()` uses `fstat()` and computes bytes from `st_blocksize * st_nblocks`. `os_phys_mem()` walks QNX syspage `asinfo` entries and sums ranges named `"ram"`. Free space uses `statvfs()`. Cache invalidation is unsupported.

## State and Persistence
No persistent state is stored. Helpers only query kernel metadata.

## Dependencies and Integration Points
It depends on QNX syspage, statvfs, CAM command, utsname, and sys/tree-interacting headers. Feature macros drive fio option availability for filesystem stats and generic random seeding while disabling normal shm headers.

## Risks and Edge Cases
The `os_phys_mem()` implementation uses C99-style loop declarations and asserts syspage element sizing. Block sizing via `st_blocksize * st_nblocks` may describe allocated blocks rather than full raw-device capacity depending on fd type. Shared-memory support is intentionally limited.

## Test Signals
QNX build tests, physical memory comparison to system tools, block/file size checks, filesystem free-space checks, and fio workloads that avoid unsupported shm paths validate this header.
