# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kvatoname.c

Kernel function-address to name resolver.

Key behavior:
- Fills `ipfunc_resolve_t` with a function pointer and calls `SIOCFUNCL`.
- Opens `IPL_NAME` unless `OPT_DONTOPEN` is set.
- Returns a static buffer containing the resolved name.

Research notes:
- Ignores ioctl failure and returns whatever name buffer contains.
- Static return storage is overwritten on each call.
