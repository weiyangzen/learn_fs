# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnatfield.c

Tabular NAT-entry field definitions and printer.

Key behavior:
- Defines `natfields[]` with names for interfaces, MTUs, checksums, counters, protocols, hashes, refs, addresses, ports, age, and direction.
- `printnatfield()` prints one selected field or all positive fields for sentinel `-2`.

Research notes:
- Field `v1` prints `nat_v[0]`, likely intended to be `nat_v[1]`.
