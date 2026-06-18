# File Research: sources/os/bsd/freebsd-src/sys/sys/signal.h

Public signal ABI header.

Key responsibilities:
- Defines standard and BSD signal numbers, including real-time signal range `SIGRTMIN` to `SIGRTMAX`.
- Defines handler values `SIG_DFL`, `SIG_IGN`, `SIG_ERR`, and `SIG_HOLD`.
- Defines `__sighandler_t`, `sigset_t`, `sigevent`, `siginfo_t`, and 32-bit siginfo compatibility layout.
- Defines `si_code` values for illegal instruction, bus error, segmentation fault, floating point exception, trap, child, and poll events.
- Defines `struct sigaction`, signal action flags, legacy `sigvec` and `sigstack`, `sigmask()`, `sigprocmask()` operations, and `signal()` declaration.
- Defines ancillary BSD extensions such as `SIGEV_KEVENT`, `SIGEV_THREAD_ID`, `SIGIO`, `SIGINFO`, and socket/queue-related signal metadata.

Important patterns:
- Visibility macros gate POSIX, XSI, and BSD interfaces.
- `siginfo_t` packs generic fields plus a union for fault, timer, message queue, poll, and Capsicum-specific reasons.
- Legacy compatibility remains in the ABI surface through old vector and sockaddr-era APIs.

Research relevance:
- Canonical userspace contract for signal delivery, handlers, masks, and async notification results.
