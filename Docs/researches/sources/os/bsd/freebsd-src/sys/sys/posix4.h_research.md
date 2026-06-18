# File Research: sources/os/bsd/freebsd-src/sys/sys/posix4.h

This header supports POSIX.1b/P1003.1b kernel facilities. It includes system parameter, ioctl, malloc, and scheduler headers, then declares module-stub support and configuration helpers.

`SYSCALL_NOT_PRESENT_GEN` generates syscall stubs that call `syscall_not_present()` for optional loadable functionality. `M_P31B` declares a malloc type. `p31b_proc()` resolves a target process by PID, and `p31b_setcfg`, `getcfg`, `iscfg`, and `unsetcfg` manage feature configuration flags.

When `_KPOSIX_PRIORITY_SCHEDULING` is enabled, the header defines scheduler operation IDs, a read/write access vector macro, an opaque `struct ksched`, and attach/detach plus set/get/yield/priority/round-robin interval methods. Filesystem relevance is low but systemic: optional POSIX kernel facilities and scheduling policy affect process behavior around I/O workloads.
