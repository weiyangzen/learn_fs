# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ip6.c

`snoopy` IPv6 decoder with extension-header skipping.

Key behavior:
- Parses IPv6 base header, payload length, next header, hop limit, source, and destination.
- Filters on source, destination, either address, or next-header value.
- `v6hdrlen()` walks hop-by-hop, routing, fragment, and destination extension headers.
- `v6hdr_seprint()` formats fragment extension header details and advances to final payload.
- Demuxes many next-header values including TCP, UDP, GRE, OSPF, and ICMPv6.

Integration:
- Reached from Ethernet EtherType `0x86dd`.

Risks and notes:
- Demux uses original base `proto`, not necessarily final next header after extension headers, so extension-header packets may be routed to the wrong decoder.
