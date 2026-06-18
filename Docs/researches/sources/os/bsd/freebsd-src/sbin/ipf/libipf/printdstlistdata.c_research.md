# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistdata.c

Destination-list metadata formatter.

Key behavior:
- Prints save/debug/normal forms for destination-list headers.
- Includes role/unit, name, policy, references, delete marker, and node-list pointer depending on options.
- Delegates policy names to `printdstlistpolicy()`.

Research notes:
- Uses `pool .../dstlist` syntax for save-style output.
