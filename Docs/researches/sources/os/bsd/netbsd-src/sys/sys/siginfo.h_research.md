# File Research: sources/os/bsd/netbsd-src/sys/sys/siginfo.h

Read completely: 286 lines.

This header defines `sigval_t`, the internal `_ksiginfo` payload, public fixed-size `siginfo_t`, kernel `ksiginfo_t`, field accessor macros, and `si_code` constants. The reason union covers realtime values, child status/times, fault addresses/traps, poll band/fd, syscall trace data, and ptrace report state.

Kernel-only helpers define queue flags, initialization macros, copy-without-queue-pointers, trap predicates, and kernel field aliases. Public constants enumerate signal-specific codes for SIGILL, SIGFPE, SIGSEGV, SIGBUS, SIGTRAP, SIGCHLD, SIGIO, and generic origins such as `SI_USER`, `SI_QUEUE`, `SI_TIMER`, and `SI_NOINFO`.

Risks: `siginfo_t` is fixed at 128 bytes for ABI expansion. Field macros alias overlapping union members, so producers must set fields matching the signal code.
