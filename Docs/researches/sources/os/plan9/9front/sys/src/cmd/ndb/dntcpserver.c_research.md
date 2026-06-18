# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dntcpserver.c

DNS-over-TCP and DNS-over-TLS server implementation, including AXFR support.

Key elements:
- `dntcpserver` forks a server process, accepts one TCP/TLS connection from `tcpannounce`, then loops reading length-prefixed DNS messages.
- Supports optional TLS server mode on port 853 using a PEM certificate chain.
- Parses incoming DNS messages, EDNS options, and hands normal questions to `dnserver`.
- Handles AXFR (`Taxfr`) specially through `dnzone`.
- `dnzone` checks the SOA, verifies the caller is local or listed in `dnsslave`, then streams SOA, zone RRs from `rrgetzone`, and final SOA.
- `findserver` resolves slave names and compares them to the caller IP.
- `tcpannounce` listens, controls child count with `/proc/pid/wait`, accepts connections, performs TLS when configured, and records remote address.

Notable behavior:
- Each accepted connection is handled in a forked child.
- Reply writes are bounded by remaining request timeout.
- AXFR authorization is tied to SOA `slaves` list and `myip`.

Risks and quirks:
- Only AXFR receives special transfer handling; IXFR remains unsupported elsewhere.
- Uses shared-memory forks and global state like the UDP server.
- Child count is capped at `Maxprocs = 64`.
