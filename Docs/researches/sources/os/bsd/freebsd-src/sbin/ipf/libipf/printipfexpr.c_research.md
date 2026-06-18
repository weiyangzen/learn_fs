# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printipfexpr.c

Pretty-printer for packed IPFilter expression arrays.

Key behavior:
- Walks the size-prefixed expression array until `IPF_EXP_END`.
- Prints IP/IPv6 address predicates, protocol, TCP/UDP ports, TCP flags/state, and idle time predicates.
- Delegates ports, scalar values, IPv4 host/mask pairs, and IPv6 host/mask pairs to helper functions.

Research notes:
- TCP flags loop compares `j < array[4]`, which appears inconsistent with `ipfe->ipfe_narg`.
