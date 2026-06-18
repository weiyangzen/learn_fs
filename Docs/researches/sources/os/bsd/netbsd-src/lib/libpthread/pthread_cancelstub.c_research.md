# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_cancelstub.c

This file provides libpthread's strong cancellation-aware wrappers around libc syscall stubs for POSIX cancellation points. It declares `_sys_*` entry points that perform raw system calls without cancellation checks, then defines public wrappers that call `TESTCANCEL(self)` before and after the raw call.

Covered wrappers include socket and I/O calls (`accept`, `accept4`, `connect`, `read`, `write`, `readv`, `writev`, `pread`, `pwrite`, `recv*`, `send*`), synchronization and waiting calls (`poll`, `pselect`, `select`, `kevent`, `sigsuspend`, `sigwait`, `wait4`, `nanosleep`, `clock_nanosleep`), filesystem sync and open calls (`close`, `open`, `openat`, `fsync`, `fdatasync`, `fsync_range`, `msync`), message queues, aio suspend, System V messages, and `tcdrain`.

`TESTCANCEL` skips checks when using libc stubs, otherwise reads `pt_cancel` relaxed, issues an acquire barrier when cancelled, and calls `pthread__cancelled`. `sigwait` preserves caller `errno` while translating the signal wait result into the POSIX return convention. Variadic `open`, `openat`, and `fcntl` forward one argument through `va_arg`.

Integration points: tied to libc symbol naming, compat prototypes, weak/strong aliases, and NetBSD versioned syscall names. Risks are ABI drift when libc adds or renames cancellation points, incorrect variadic forwarding for command-specific `fcntl` arguments, and maintaining exact errno/cancellation semantics.
