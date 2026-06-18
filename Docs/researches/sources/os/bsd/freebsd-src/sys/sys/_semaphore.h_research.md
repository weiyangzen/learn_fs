# File Research: sources/os/bsd/freebsd-src/sys/sys/_semaphore.h

Kernel semaphore user ABI declarations.

Key elements:
- Defines `semid_t` as `intptr_t`.
- Defines `SEM_VALUE_MAX`.
- Outside `_KERNEL`, declares `ksem_*` APIs for close, post, wait, timedwait, init, open, unlink, getvalue, and destroy.

Dependencies:
- Forward-declares `struct timespec`.
- Uses `mode_t` from including context.

Research notes:
- Provides low-level FreeBSD kernel semaphore syscall interface declarations, distinct from higher-level POSIX wrappers.
