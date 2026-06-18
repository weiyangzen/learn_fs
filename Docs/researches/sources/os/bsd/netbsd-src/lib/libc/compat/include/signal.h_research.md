# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/signal.h

Declares old signal ABI types and functions.

It includes `<compat/sys/signal.h>`, declares old and modern variants for `sigaction`, signal-set manipulation, `sigpending`, `sigprocmask`, `sigsuspend`, timed signal wait, `sigaltstack`, and trampoline symbols derived from `__SIGTRAMP_*_VERSION`.

This header is the central libc compatibility surface for legacy signal behavior.
