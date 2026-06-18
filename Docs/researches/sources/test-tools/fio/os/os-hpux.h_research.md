# sources/test-tools/fio/os/os-hpux.h

## Purpose
`os-hpux.h` adapts fio to HP-UX, including direct I/O capability, POSIX advice mappings, AIO control-block type selection, block/char device sizing, physical memory, and CPU count.

## Important APIs, Types, and Functions
It defines `FIO_HAVE_ODIRECT`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_USE_GENERIC_SWAP`, `FIO_OS_HAVE_AIOCB_TYPEDEF`, `os_aiocb_t` as `struct aiocb64`, and `FIO_HAVE_CPU_CONF_SYSCONF`. Inline helpers are `blockdev_invalidate_cache()`, `blockdev_size()`, `chardev_size()`, `os_phys_mem()`, and `cpus_configured()`.

## Control Flow
`blockdev_size()` calls `ioctl(DIOC_DESCRIBE_EXT)` and combines high/low max SVA fields with logical block size. `os_phys_mem()` uses `pstat(PSTAT_STATIC)` and multiplies physical pages by page size. `cpus_configured()` uses `mpctl(MPC_GETNUMSPUS)`.

## State and Persistence
There is no persistent state. Helpers query kernel/device properties; cache invalidation is unsupported.

## Dependencies and Integration Points
It relies on HP-UX fadvise/mman/mpctl/diskio/pstat/AIO headers and fio `file.h`. Its macros drive option availability for direct I/O, char-device sizing, generic random seeds, and POSIX AIO typedef handling.

## Risks and Edge Cases
Device size computation depends on HP-UX disk descriptor fields and may not apply to all device types. `MSG_WAITALL` is locally defined if missing. CPU count and memory queries can return unusual values on partitioned systems.

## Test Signals
HP-UX build/link coverage, POSIX AIO builds, disk size comparisons, physical memory keyword checks, and direct-I/O job smoke tests validate this header.
