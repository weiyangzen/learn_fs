# File Research: sources/os/bsd/openbsd-src/sbin/route/show.h

This header defines shared route display interfaces and sockaddr storage.

Key declarations:
- `union sockunion`: overlays generic, IPv4, IPv6, link-layer, route-label, MPLS, and storage sockaddrs.
- Display/query functions: `printsource`, `get_rtaddrs`, `p_rttables`, `p_sockaddr`, `routename`, `netname`, `mpls_op`, `get_sysctl`.
- Shared globals: `nflag`, `Fflag`, `verbose`, and `so_label`.
- `PLEN` constant for prefix display width.

Integration:
- Included by both `route.c` and `show.c` to share routing output helpers and common sockaddr storage.

Risk notes:
- The header exposes globals rather than an explicit context object, matching the utility’s single-process command style.
