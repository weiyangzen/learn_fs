# sources/test-tools/fio/os/os-freebsd.h

## Purpose
`os-freebsd.h` supplies fio's FreeBSD feature declarations and inline wrappers for CPU affinity, disk sizing, trim, physical memory, filesystem free space, and thread id.

## Important APIs, Types, and Functions
It defines feature macros for direct I/O, generic random seeds, character device size, filesystem stats, trim, gettid, CPU affinity, and removed-shm attachment. Helpers include cpuset initialization/destruction, CPU bit operations, `fio_setaffinity()`, `fio_getaffinity()`, `blockdev_size()`, `chardev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, `get_fs_free_size()`, `os_trim()`, and `shm_attach_to_open_removed()`.

## Control Flow
Affinity uses FreeBSD `cpuset_setaffinity()` and `cpuset_getaffinity()`. Disk size uses `DIOCGMEDIASIZE`; trim sends `DIOCGDELETE` with an offset/length pair. Memory and removed-shm support are read through `sysctl`; free space uses `statvfs()`.

## State and Persistence
No static state is stored. Affinity calls change scheduler state for a process/thread target, and trim can persistently discard device ranges.

## Dependencies and Integration Points
The header depends on FreeBSD `sysctl`, disk, threading, socket, param, cpuset, and statvfs APIs. The macros enable fio's direct I/O, trim verification, affinity options, filesystem stats, and shared-memory behavior checks.

## Risks and Edge Cases
`fio_getaffinity()` uses `CPU_WHICH_PID` while `fio_setaffinity()` uses `CPU_WHICH_TID`, so pid/tid interpretation matters. Cache invalidation is unsupported. Trim ioctl semantics should be tested across FreeBSD releases and device classes.

## Test Signals
FreeBSD build coverage, `cpus_allowed` parsing and enforcement, block/char device size checks, disposable-device trim, and `shm_attach_to_open_removed()` on kernels with different `kern.ipc.shm_allow_removed` values are useful.
