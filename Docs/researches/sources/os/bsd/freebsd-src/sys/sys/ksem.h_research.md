# File Research: sources/os/bsd/freebsd-src/sys/sys/ksem.h

Internal POSIX semaphore file-object structure header, only available to kernel or `_WANT_FILE` consumers. `struct ksem` contains refcount, mode, owner ids, semaphore value, condition variable, waiter count, flags, timestamps for file-stat behavior, MAC label, and optional path.

Flags mark anonymous semaphores and dead semaphores that reject new waiters.
