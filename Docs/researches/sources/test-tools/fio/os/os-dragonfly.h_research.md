# sources/test-tools/fio/os/os-dragonfly.h

## Purpose
`os-dragonfly.h` adapts fio to DragonFly BSD. It declares supported features and implements CPU masks/affinity, I/O priority mapping, block/character device sizing, trim, filesystem free-space, physical memory, thread id, and removed-shm attachment behavior.

## Important APIs, Types, and Functions
It defines `FIO_HAVE_ODIRECT`, `FIO_HAVE_FS_STAT`, `FIO_HAVE_TRIM`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_HAVE_GETTID`, `FIO_HAVE_CPU_AFFINITY`, `FIO_HAVE_IOPRIO`, and `FIO_HAVE_SHM_ATTACH_REMOVED`. Helpers include `fio_cpuset_init()`, `fio_cpu_set()/clear()/isset()/count()`, `fio_setaffinity()`, `fio_getaffinity()`, `blockdev_size()`, `chardev_size()`, `os_trim()`, `get_fs_free_size()`, `os_phys_mem()`, `gettid()`, and `shm_attach_to_open_removed()`.

## Control Flow
Affinity is implemented with DragonFly `usched_set()` for the current thread only, adding CPUs one by one. Device size uses `DIOCGPART`; trim uses `DAIOCTRIM` or legacy `IOCTLTRIM`; free space uses `statvfs()`. Shared-memory behavior is queried from `kern.ipc.shm_allow_removed`.

## State and Persistence
The header has no static state. Calls can change thread CPU binding and issue device trim commands; other helpers query kernel state.

## Dependencies and Integration Points
It depends on DragonFly `sysctl`, `statvfs`, disk-slice, scheduler, and resource headers. Its feature macros enable fio options and code paths for affinity, trim, ioprio, direct I/O, and filesystem stats.

## Risks and Edge Cases
Affinity ignores the passed pid and applies to the current thread because of `usched_set()` limitations. The cpumask compatibility macros assume DragonFly's x86_64 layout for older headers. I/O priority has no class concept, so fio's class/hint arguments are collapsed to a simple priority value.

## Test Signals
DragonFly build tests, affinity set/get for current thread, trim against disposable block devices, sysctl-based memory/free-space checks, and ioprio option parsing are relevant.
