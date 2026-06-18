# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_net_ntop.c

Implements `inet_net_ntop`, converting network numbers to CIDR presentation format.

Behavior:
- IPv4 validates bits `0..32`, prints whole octets and masked partial octet, always appending `/bits`.
- IPv6 validates bits `0..128`, zeroes host bits in a private buffer, compresses zero runs, detects IPv4-mapped/compatible forms, and appends `/bits`.
- Unsupported families set `EAFNOSUPPORT`; bad buffer space sets `EMSGSIZE`.

Difference from `inet_cidr_ntop`: this represents network numbers and masks/omits host bits.
