# sources/test-tools/fio/os/os-linux.h

## Purpose
`os-linux.h` is fio's Linux and Android platform adapter. It declares Linux feature availability and provides wrappers for CPU affinity, I/O priorities, device sizing, cache invalidation, memory/free-space queries, trim, scheduling, byte swaps, pwritev2/preadv2, fallocate, and CPU feature probing.

## Important APIs, Types, and Functions
The header defines many `FIO_HAVE_*` capabilities, `os_cpu_mask_t`, CPU mask macros, ioprio classes and encoding helpers, `ioprio_set()`, `gettid()`, `blockdev_invalidate_cache()`, `blockdev_size()`, `os_phys_mem()`, `arch_cache_line_size()`, `get_fs_free_size()`, `os_trim()`, `fio_set_sched_idle()`, fallback `preadv2()`/`pwritev2()`, `shm_attach_to_open_removed()`, `fio_fallocate()`, and `os_cpu_has()`.

## Control Flow
Affinity maps to `sched_setaffinity()`/`sched_getaffinity()` according to configure-detected signatures. I/O priority is encoded with class, hint, and level before the `__NR_ioprio_set` syscall. Device size and trim use `BLKGETSIZE64`, `BLKFLSBUF`, and `BLKDISCARD` ioctls. Cache line size reads sysfs. Free space uses `statfs()`. `preadv2()`/`pwritev2()` wrappers split 64-bit offsets for 32-bit ABIs. CPU feature probing checks AArch64 HWCAP bits for CRC crypto.

## State and Persistence
The header has no static state. Helpers can change thread scheduling, affinity, I/O priority, allocate file space, discard block ranges, or invalidate block-device cache. Other helpers only query kernel state.

## Dependencies and Integration Points
It depends on Linux ioctl, syscall, mmap, sched, fs, SCSI generic, byteorder, Android ashmem, fio `file.h`, and architecture headers. Its feature macros drive the options table, engines, trim support, disk utilization, cgroups, pwritev2 flags, write hints, atomic writes, and CPU-specific checksum paths.

## Risks and Edge Cases
Kernel headers and libc may disagree on newer constants; this header supplies many fallback definitions. `FIO_HAVE_RWF_ATOMIC` is declared with fallback `RWF_ATOMIC`, but runtime support still depends on kernel/filesystem behavior. Sysfs cache-line reading can fail and must fall back in `os.h`. `fallocate()` has a workaround for old glibc returning positive errno values.

## Test Signals
Linux builds across glibc/musl/Android, affinity and ioprio option tests, block-device size/cache/trim tests, pwritev2 flag tests, cgroup/disk-util jobs, fallocate modes, and CPU feature detection on AArch64 are strong signals.
