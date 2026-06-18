# File Research: sources/os/bsd/netbsd-src/sys/sys/signal.h

Read completely: 342 lines.

This public signal header defines signal numbers 1 through 63, handler sentinel values, signal-set macro remapping for the kernel, `struct sigaction`, signal trampoline version constants, signal action flags, `sigprocmask` commands, alternate stack constants, `struct sigstack`, `struct sigevent`, and userland signal APIs.

It conditionally exposes POSIX/XOpen/NetBSD features according to feature-test macros. It includes architecture signal definitions and documents NetBSD's trampoline ABI versions: historical kernel sigcode, legacy sigcontext, and modern siginfo trampolines.

Userland prototypes include `signal`, `sigqueue`, legacy `bsd_signal` under relevant standards modes, and NetBSD `sigqueueinfo`.

Risks: this is central process ABI. Trampoline version constants must match libc and machine-dependent signal frame code; feature-test gating affects which symbols and types user code sees.
