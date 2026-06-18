# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printiphdr.c

Compact IPv4 header debug printer.

Key behavior:
- Prints version, header length, total length, TOS, fragment offset, checksum, source, and destination in one line prefix.

Research notes:
- Does not close the opening `ip(`; callers likely append more fields.
