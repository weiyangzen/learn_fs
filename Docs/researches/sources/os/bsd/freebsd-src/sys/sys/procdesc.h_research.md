# File Research: sources/os/bsd/freebsd-src/sys/sys/procdesc.h

Read completely: 145 lines.

## Purpose
Defines process descriptor kernel state and userland process-descriptor syscalls for fd-based process lifecycle control.

## Main Elements
- In-kernel `struct procdesc` links one process to one process-descriptor file, caches pid, tracks refcount, exit status, flags, selinfo notification, and a mutex.
- Defines lock macros for process descriptor mutex lifecycle and access.
- Defines descriptor state flags `PDF_CLOSED`, `PDF_EXITED`, and `PDF_DAEMON`.
- Declares kernel helpers for procdesc exit notification, fd lookup, pid retrieval, creation, file initialization, reaping, and allocation.
- Declares userland syscalls `pdfork`, `pdrfork`, `pdkill`, `pdgetpid`, `pdwait`, and `pdrfork_thread`.
- Defines user flags `PD_DAEMON`, `PD_CLOEXEC`, and `PD_ALLOWED_AT_FORK`.

## Dependencies And Integration
Integrates with process lifetime, file descriptors, Capsicum rights, `selinfo`/poll/kqueue notification, proctree locking, and wait/reap behavior.

## Risk Notes
The invariant of one process descriptor per process is central. Lifetime is split between process and file references, so refcounting, close-vs-exit races, and notification state must stay consistent.
