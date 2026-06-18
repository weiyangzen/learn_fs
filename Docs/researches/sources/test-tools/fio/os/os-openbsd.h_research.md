# sources/test-tools/fio/os/os-openbsd.h

## Purpose
`os-openbsd.h` adapts fio to OpenBSD with feature declarations and helpers for disk sizing, memory, thread id, filesystem free space, removed shared-memory behavior, byte swaps, and optional thread affinity query.

## Important APIs, Types, and Functions
It defines `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_FS_STAT`, `FIO_HAVE_GETTID`, `FIO_HAVE_SHM_ATTACH_REMOVED`, `OS_MAP_ANON`, swap macros, optional `FIO_HAVE_GET_THREAD_AFFINITY`, and helpers `blockdev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, `get_fs_free_size()`, and `shm_attach_to_open_removed()`.

## Control Flow
Disk size uses `ioctl(DIOCGDINFO)` and disklabel fields. Memory uses `sysctl(CTL_HW, HW_PHYSMEM64)`. `gettid()` casts `pthread_self()`. `shm_attach_to_open_removed()` parses `uname().release` and returns true for OpenBSD 5.1 or newer.

## State and Persistence
There is no static state. Helpers query OS state; cache invalidation is unsupported.

## Dependencies and Integration Points
It depends on OpenBSD disklabel, dkio, endian, utsname, sysctl, statvfs, and fio `file.h`. It undefines `RB_*` names to avoid tree macro conflicts with fio headers.

## Risks and Edge Cases
Version parsing assumes single-digit major/minor release components; the code explicitly rejects unexpected formats. OpenBSD lacks direct I/O and trim declarations here, so common option availability must reflect that. `pthread_self()` as integer thread id is a compatibility approximation.

## Test Signals
OpenBSD build tests, disk/free-space/memory query tests, release parsing across supported versions, and shared-memory removal behavior checks are useful.
