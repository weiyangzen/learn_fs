# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printmask.c

Network mask printer.

Key behavior:
- IPv6 masks print as prefix length from `count6bits()`.
- IPv4 contiguous masks print as prefix length from `count4bits()`.
- Non-contiguous IPv4 masks print as dotted mask.

Research notes:
- Does not special-case invalid IPv6 masks beyond whatever `count6bits()` returns.
