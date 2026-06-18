# File Research: sources/os/bsd/freebsd-src/sys/sys/signalvar.h

Kernel-private signal state, queues, and delivery interfaces.

Key responsibilities:
- Defines `struct sigacts`, the per-process signal action table and masks for catch, ignore, reset, on-stack, interrupt, no-defer, and siginfo behavior.
- Provides signal-set manipulation macros such as `SIGADDSET`, `SIGDELSET`, `SIGEMPTYSET`, `SIGFILLSET`, `SIGSETOR`, `SIGSETAND`, and compatibility conversions.
- Defines `ksiginfo_t` and `sigqueue_t` for queued signal metadata and pending signal masks.
- Defines fast signal blocking commands and flags.
- Declares kernel signal delivery, queue, action, trap, ptrace, async I/O, and process-exit routines.

Important patterns:
- `sigacts` has mutex and refcount fields last because `sigacts_copy()` relies on copying the preceding state as a block.
- Pending state is split between thread and process signal queues.
- `SIGPENDING()` checks both thread and process pending sets against the thread mask.
- `KSI_*` flags classify trap, external, sigqueue, ptrace, direct insertion, and exception-generated signals.
- `SIGIO_LOCK()` protects async I/O signal ownership structures.

Research relevance:
- Core map of FreeBSD's in-kernel signal lifecycle: action state, pending queues, delivery selection, and cleanup.
