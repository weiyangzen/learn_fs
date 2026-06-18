# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printip.c

IP address printer for pool/hash output.

Key behavior:
- IPv4 values below 256 are printed as decimal numbers; other IPv4 values as dotted quads.
- IPv6 values are printed with `inet_ntop()` when enabled.
- Unknown families print `?(family)?`.

Research notes:
- The small-IPv4 decimal behavior supports numeric table identifiers or compact address syntax.
