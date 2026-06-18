# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistnode.c

Destination-list node formatter.

Key behavior:
- Copies the fixed header, then copies the full variable-sized node.
- Field mode prints selected fields via `printpoolfield()`.
- Normal mode prints optional interface name, address, and semicolon.
- Debug mode prints interface, address, state/ref/name/uid details.

Research notes:
- On full-node copy failure, allocated memory is not freed before return.
