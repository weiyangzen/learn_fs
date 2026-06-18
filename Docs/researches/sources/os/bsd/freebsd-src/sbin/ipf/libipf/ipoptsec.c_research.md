# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipoptsec.c

IPv4 security classification lookup helpers.

Key behavior:
- Defines `secclass[]` mapping textual IPSO classes to option values and match bits.
- `seclevel()` converts a text name to the IPSO class value.
- `secbit()` converts a class value to the corresponding bit.

Research notes:
- Unknown classes print diagnostics and return zero.
