# File Research: sources/os/bsd/freebsd-src/sys/sys/hwt.h

User-visible Hardware Trace header defining ioctl commands and ABI structs for allocating, starting, stopping, configuring, servicing, and reading hardware trace sessions. It depends on `sys/hwt_record.h`, `cpuset_t`, VM offsets, and path limits.

The ioctl API uses magic `0x42` and exposes `HWT_IOC_ALLOC`, `START`, `STOP`, `RECORD_GET`, `BUFPTR_GET`, `SET_CONFIG`, `WAKEUP`, and `SVC_BUF`. Sessions can be per-thread (`HWT_MODE_THREAD`) or per-CPU (`HWT_MODE_CPU`) and identify a backend by name.

ABI structures are explicitly 16-byte aligned. `struct hwt_alloc` includes buffer size, mode, pid/cpuset, backend name, returned identity, and kqueue fd. `struct hwt_record_user_entry` mirrors record types for mmap/executable/kernel path records, buffer records, and thread records.
