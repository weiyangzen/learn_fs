# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/verbose.c

Verbose-output helpers.

Key behavior:
- `verbose()` prints through `vprintf()` when global `opts` includes `OPT_VERBOSE`.
- `ipfkverbose()` attempts to route verbose kernel-style messages through `verbose()`.

Research notes:
- `ipfkverbose()` passes a `va_list` as a normal variadic argument to `verbose()`, so it does not actually forward formatting arguments correctly.
