# File Research: sources/os/bsd/netbsd-src/sys/sys/lock.h

Defines common spinlock backoff and kernel lock declarations around machine lock primitives. It imports `machine/lock.h`, supplies default spin hook/backoff hook/min/max values, the `SPINLOCK_BACKOFF` macro, optional LOCKDEBUG spinout behavior, and `kernel_lock[]`.

This is low-level synchronization infrastructure. Risks are architecture hook correctness, backoff behavior under contention, and LOCKDEBUG-only spinout diagnostics changing failure visibility.
