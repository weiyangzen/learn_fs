# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhostmask.c

Host-plus-mask printer.

Key behavior:
- Prints `any` when family is unknown or both address and mask are zero.
- Prints address through IPv4/IPv6 formatting and appends mask with `printmask()`.

Research notes:
- IPv6 formatting depends on `USE_INET6`.
