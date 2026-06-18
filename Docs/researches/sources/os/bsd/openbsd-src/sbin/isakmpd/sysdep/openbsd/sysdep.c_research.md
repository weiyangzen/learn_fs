# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/sysdep/openbsd/sysdep.c

This OpenBSD-specific file provides socket policy bypass setup for isakmpd control traffic.

Key API:
- `sysdep_cleartext(int fd, int af)`: forces communication on a socket to bypass IPsec policy so IKE/key-management packets travel in cleartext.

Behavior and integration:
- No-ops when `app_none` is set.
- Supports `AF_INET` and `AF_INET6`.
- Applies `IPSEC_LEVEL_BYPASS` through monitored `setsockopt` calls for auth, ESP transport, ESP network, and optionally IPCOMP levels.
- Uses `monitor_setsockopt()` rather than direct `setsockopt`, consistent with privilege separation.

Risk notes:
- Unsupported address families fail with logging.
- IPCOMP option absence is tolerated only for `ENOPROTOOPT`; other errors fail setup.
