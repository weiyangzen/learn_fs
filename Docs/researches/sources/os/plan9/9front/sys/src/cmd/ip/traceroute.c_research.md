# File Research: sources/os/plan9/9front/sys/src/cmd/ip/traceroute.c

This is a Plan 9 traceroute utility built around network control/data files.

Key behavior:
- Parses dial strings with optional netdir/protocol and defaults to `/net`, `tcp`, and port 32767.
- Uses the connection server to translate names unless bypassed or unavailable.
- Probes TCP/IL by attempting connect, UDP by writing to a likely-unused port, and ICMP/ICMPv6 by sending echo requests.
- Sets TTL through the connection control file and times each probe in microseconds.
- Optionally reverse-resolves hop names and prints latency low/avg/high plus optional histograms.

Research notes:
- Handles Plan 9 error strings such as `ttl exceeded at`, `refused`, and `unreachable`.
- Probe count defaults to three and TTL stops at 31.
