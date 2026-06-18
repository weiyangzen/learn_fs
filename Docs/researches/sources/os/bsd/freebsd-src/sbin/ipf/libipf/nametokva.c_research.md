# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/nametokva.c

Kernel function-name to address resolver.

Key behavior:
- Fills `ipfunc_resolve_t` with a function name and calls `SIOCFUNCL`.
- Opens `IPL_NAME` unless `OPT_DONTOPEN` is set.
- Returns `(ipfunc_t)-1` when the resolved address is still NULL.

Research notes:
- The name is copied with `strncpy()` without explicit forced NUL termination.
