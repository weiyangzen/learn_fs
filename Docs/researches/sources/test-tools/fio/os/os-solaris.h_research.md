# sources/test-tools/fio/os/os-solaris.h

## Purpose
`os-solaris.h` adapts fio to Solaris. It declares platform features and implements char-device sizing, generic block sizing, direct I/O enabling, physical memory/free-space queries, processor-set based affinity, ctime compatibility, and thread id support.

## Important APIs, Types, and Functions
It defines `FIO_HAVE_CPU_AFFINITY`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_USE_GENERIC_BDEV_SIZE`, `FIO_HAVE_FS_STAT`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_GETTID`, `FIO_OS_DIRECTIO`, `FIO_MAX_CPUS`, `os_cpu_mask_t` as `psetid_t`, `struct solaris_rand_seed`, and helpers `chardev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `get_fs_free_size()`, `fio_set_odirect()`, `fio_cpu_isset()`, `fio_cpu_count()`, `fio_cpuset_init()`, `fio_cpuset_exit()`, and `gettid()`.

## Control Flow
Character-device size uses `DKIOCGMEDIAINFO`. Direct I/O calls `directio(fd, DIRECTIO_ON)`. Affinity creates processor sets, assigns CPUs with `pset_assign()`, binds LWPs with `pset_bind()`, and counts/tests membership with `pset_info()`. Free space uses `statvfs()` and memory uses `sysconf()`.

## State and Persistence
Processor sets are OS resources created/destroyed by cpuset helpers. Direct I/O changes fd behavior. Other helpers query state; cache invalidation is unsupported.

## Dependencies and Integration Points
It depends on Solaris pset, dkio, byteorder, statvfs, mmap, pthread, and directio APIs. Its feature macros enable fio affinity options, direct I/O setup, filesystem stats, char-device sizing, and generic block-size logic.

## Risks and Edge Cases
Processor-set creation can fail and must be destroyed to avoid leaks. `fio_cpu_clear()` and `fio_cpu_set()` have side effects on global processor-set assignment, not just local masks. `gettid()` returns `pthread_self()` cast to int-like return, which may be lossy depending on type width.

## Test Signals
Solaris build tests, processor-set lifecycle tests, directio jobs, DKIO media-size checks, statvfs free-space checks, and CPU affinity option tests are important.
