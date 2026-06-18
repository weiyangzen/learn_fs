# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/print_toif.c

Printer for `to`, `dup-to`, and `reply-to` rule destinations.

Key behavior:
- Handles normal interface destinations, destination-list destinations, and unknown destination types.
- Prints unresolved interface markers with `(!)`.
- Appends IPv4/IPv6 next-hop addresses when present.

Research notes:
- Resolves names as offsets into the rule’s packed name buffer.
