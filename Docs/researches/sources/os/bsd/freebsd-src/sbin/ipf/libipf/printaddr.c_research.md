# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printaddr.c

Generic rule address printer.

Key behavior:
- Handles dynamic interface, broadcast, network, peer, lookup, normal, range, and split address types.
- Delegates concrete host/mask output to `printhostmask()`, `printhost()`, and `printlookup()`.
- Prints interface-derived suffixes such as `/bcast`, `/net`, and `/peer`.

Research notes:
- Unknown address types are printed numerically with a mask.
