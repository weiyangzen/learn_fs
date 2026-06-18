# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnataddr.c

NAT address formatter.

Key behavior:
- Handles IPv4 zero-address normal form as `0/prefix`.
- Delegates other IPv4 and IPv6 NAT address forms to `printaddr()`.
- Prints unknown versions as `{v=n}`.

Research notes:
- Includes `kmem.h` but does not use kernel-memory helpers directly.
