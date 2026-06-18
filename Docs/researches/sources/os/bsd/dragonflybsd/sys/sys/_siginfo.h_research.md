# File Research: sources/os/bsd/dragonflybsd/sys/sys/_siginfo.h

Read completely: 142 lines.

This header defines POSIX/XSI signal payload types and `si_code` constants.

Key contents:
- Declares `pid_t` and `uid_t` if needed.
- Defines `union sigval`.
- Defines generic `SI_*` codes and signal-specific codes for `SIGILL`, `SIGFPE`, `SIGSEGV`, `SIGBUS`, `SIGTRAP`, `SIGCHLD`, and `SIGPOLL`.
- Defines `siginfo_t` with signal number, errno, code, sender pid/uid, status, fault address, signal value, band event, and spare fields.

Security/reliability notes:
- No runtime logic. Layout and visibility are ABI-sensitive for signal delivery, `sigqueue`, timers, async I/O, and user handlers.
