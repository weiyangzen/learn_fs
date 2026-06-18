# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ip6.c

This module decodes IPv6 headers, selected extension headers, and demuxes by final next-header value. The mux table includes TCP, UDP, GRE, ICMPv6, IL, and many generic IP protocol numbers.

Filters support source, destination, either address, and protocol. `v6hdrlen` walks hop-by-hop, routing, fragment, and destination extension headers to locate the final next header and payload offset.

`p_seprint` truncates to IPv6 payload length, prints source, destination, hop limit, initial next header, and payload length, then calls `v6hdr_seprint`. That helper prints fragment-header details and advances across extension headers before demuxing to the final protocol.

Malformed extension lengths set the next protocol to `dump`.
