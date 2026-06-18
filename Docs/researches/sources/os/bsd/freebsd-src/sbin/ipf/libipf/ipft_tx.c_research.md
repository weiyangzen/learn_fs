# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_tx.c

Text packet-description backend for IPFilter test tooling.

Key behavior:
- Exports `iptext` as an `ipread` provider with checksum recomputation requested.
- Parses lines into synthetic IPv4 or IPv6 packets.
- Supports direction, optional interface, protocol, source/destination addresses, ports, TCP flags, TCP sequence/ack, ICMP types/codes, and IPv4 options.
- Resolves hostnames and service names through helper APIs.

Research notes:
- Parser mutates token strings in place with `strtok()` and comma splitting.
- IPv6 support is conditional on `USE_INET6`.
