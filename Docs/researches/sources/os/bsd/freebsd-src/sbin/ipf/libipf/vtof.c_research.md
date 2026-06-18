# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/vtof.c

IP version to address-family converter.

Key behavior:
- Maps version 4 to `AF_INET`.
- Maps version 6 to `AF_INET6` when IPv6 support is compiled.
- Maps version 0 to `AF_UNSPEC`.
- Returns `-1` for unknown versions.

Research notes:
- Small utility used where structures store IP version instead of socket family.
