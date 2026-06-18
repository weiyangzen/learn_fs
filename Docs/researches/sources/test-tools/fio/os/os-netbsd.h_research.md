# sources/test-tools/fio/os/os-netbsd.h

## Purpose
`os-netbsd.h` provides fio's NetBSD platform feature declarations and helpers for disk sizing, cache invalidation status, physical memory, thread id, filesystem free space, byte swaps, and optional thread affinity query.

## Important APIs, Types, and Functions
It defines `FIO_HAVE_ODIRECT`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_FS_STAT`, `FIO_HAVE_GETTID`, `OS_MAP_ANON`, swap macros, and optional `FIO_HAVE_GET_THREAD_AFFINITY`. Inline helpers include `blockdev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, and `get_fs_free_size()`.

## Control Flow
`blockdev_size()` reads `struct disklabel` through `ioctl(DIOCGDINFO)` and multiplies sectors by sector size. `os_phys_mem()` uses `sysctl(CTL_HW, HW_PHYSMEM64)`. `gettid()` uses `_lwp_self()` when no configured gettid exists. Free space uses `statvfs()`.

## State and Persistence
There is no persistent state. Helpers query kernel/device state; cache invalidation is unsupported.

## Dependencies and Integration Points
It depends on NetBSD LWP, disklabel, dkio, endian, sysctl, and statvfs headers. It also undefines rbtree names to avoid conflicts with fio's own rbtree definitions.

## Risks and Edge Cases
Disklabel sizing may be insufficient for newer or nontraditional devices. Lack of `FIO_HAVE_TRIM` means trim-related options should be unsupported through common code. Header symbol conflict workarounds must stay aligned with NetBSD system headers.

## Test Signals
NetBSD build tests, disk size checks, filesystem free-space checks, and workloads using direct I/O and generic random seeds are useful.
