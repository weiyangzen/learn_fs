# File Research: sources/os/bsd/netbsd-src/lib/librt/Makefile

Read completely: 63 lines.

Builds NetBSD `librt` from `sem.c`, `shm.c`, and `pset.c`, plus generated syscall stubs included from `sys/Makefile.inc`. It disables sanitizers, sets warning level, includes libc internal include handling, and has a powerpc64 workaround adding libc `_errno.c`.

The installed manuals and links cover POSIX AIO, message queues, processor sets, scheduler APIs, shared memory, and semaphores, even though many syscall wrappers are generated assembly rather than C in this directory.
