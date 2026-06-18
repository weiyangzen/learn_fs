# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printunit.c

IPFilter unit/minor-name printer.

Key behavior:
- Maps log/unit constants for ipf, nat, state, auth, sync, scan, lookup, count, and all.
- Prints unknown numeric units as `unknown(n)`.

Research notes:
- Used across pool/hash/destination-list metadata output.
