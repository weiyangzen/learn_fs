# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_cidr_ntop.c

Implements `inet_cidr_ntop`, converting IPv4/IPv6 binary addresses plus prefix length to CIDR presentation format.

Behavior:
- Dispatches on `AF_INET` and `AF_INET6`; unsupported families set `EAFNOSUPPORT`.
- IPv4 accepts bits `-1..32`; `-1` suppresses `/bits`.
- IPv6 accepts bits `-1..128`, compresses longest zero run, and supports embedded IPv4 rendering.
- Uses `ADDC`/`ADDS` macros for checked appends; buffer overflow sets `EMSGSIZE`.
- Unlike `inet_net_ntop`, it may preserve nonzero host parts because CIDR host addresses are allowed.

Dependencies: `port_before.h`, `port_after.h`, `namespace.h`, inet/nameser headers.
