# File Research: sources/os/plan9/plan9/sys/src/9/ip/igmp.c

Implements an unfinished IGMPv1-style multicast group management protocol.

Key responsibilities:
- Defines IGMP packet format, report scheduling structures, global report state, and basic stats.
- `igmpsendreport` builds and sends a membership report to the all-systems multicast address with TTL 1.
- `igmpproc` sleeps until reports are queued, walks report lists, waits randomized tick counts, sends pending reports, and frees completed multicast entries.
- `igmpiput` validates incoming IGMP length, version/type, checksum, handles queries by scheduling reports for multicast groups, and handles reports by suppressing duplicate local reports for the same group.
- `igmpstats` returns query/report receive/send counts.
- `igmpinit` registers protocol `igmp`, installs `igmpreportfn`, and starts the report process.

Notable constraint:
- File header explicitly marks the implementation unfinished.
