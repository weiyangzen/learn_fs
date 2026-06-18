# File Research: sources/os/bsd/openbsd-src/sys/sys/signal.h

Public signal numbers, masks, actions, alternate stack ABI, and prototypes.

This header defines OpenBSD signal numbers 1 through 32, `_NSIG`, default/ignore/error handler sentinels, `sigset_t`, `struct sigaction`, action flags, `sigprocmask` operations, BSD `sig_t` and `struct sigvec` compatibility, `sigmask()`, and alternate signal stack types and constants. Visibility gates expose BSD, POSIX, XPG, and POSIX.1-2024 additions such as `SOCK_CLOFORK` elsewhere and `SIGWINCH` here.

It includes `<machine/signal.h>` for machine signal context and exposes the historical `signal()` prototype outside the kernel.

Filesystem/storage relevance: indirect but operationally important. Signals interrupt blocking filesystem, pipe, socket, and device operations; `SIGXFSZ` is the user-visible signal for file-size resource-limit violations.
