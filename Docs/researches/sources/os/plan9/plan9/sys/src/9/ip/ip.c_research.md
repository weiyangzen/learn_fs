# File Research: sources/os/plan9/plan9/sys/src/9/ip/ip.c

Implements core IPv4 stack operations plus shared IP initialization.

Key responsibilities:
- Initializes IPv4/IPv6 fragment pools and IPv6 parameter defaults.
- Tracks MIB-II style IP counters.
- `iprouting` toggles forwarding behavior.
- `ipoput4` performs IPv4 output: length validation, route lookup, gateway/interface selection, TTL/TOS/header setup, checksum generation, MTU selection, DF handling, fragmentation, and medium write.
- `ipiput4` performs IPv4 input: version dispatch to IPv6 if needed, header pullup, checksum validation, local-address check, option stripping for local delivery, forwarding path, TTL exceeded handling, optional reassembly before forwarding, local fragment reassembly, and protocol dispatch.
- `ip4reassemble` maintains reassembly queues keyed by source/destination/id, trims overlaps, times out old queues, and returns complete packet block lists.
- `ipfragfree4` and `ipfragallo4` manage IPv4 fragment queue allocation.
- `ipcsum` computes IPv4 header checksums.

Notable design:
- Route results may be cached in `Conv`.
- Fragment metadata is stored in space before block data using `Ipfrag`.
