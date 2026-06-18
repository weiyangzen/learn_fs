# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_posix4_mib.c

This file defines the POSIX.1b sysctl MIB backing store and exposes each configured facility as a read-only sysctl under `_p1003_1b`.

Core behavior:
- `facility[]` stores integer values indexed by `CTL_P1003_1B_*` IDs.
- The `P1B_SYSCTL()` macro defines individual read-only sysctls for asynchronous I/O, mapped files, memlock, memory protection, message passing, prioritized I/O, priority scheduling, realtime signals, semaphores, fsync, shared memory objects, synchronized I/O, timers, AIO limits, page size, realtime signal counts, semaphore counts, signal queue counts, and timer counts.
- `p31b_setcfg()` updates a facility value when the ID is valid.

Filesystem/storage relevance:
- Exposes POSIX support metadata including `fsync`, mapped files, asynchronous/prioritized/synchronized I/O, and shared memory, which are relevant to filesystem capability discovery from userland.
