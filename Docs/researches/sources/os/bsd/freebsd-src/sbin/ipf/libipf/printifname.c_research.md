# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printifname.c

Interface-name formatter.

Key behavior:
- Prints a prefix format string and interface name.
- Adds `(!)` when the interface pointer is NULL and name is neither `-` nor `*`.

Research notes:
- Used to indicate unresolved interfaces in rule output.
