# File Research: sources/os/plan9/plan9/sys/src/9/ip/udp.c

## Purpose
Implements Plan 9 UDP for IPv4 and IPv6, exposing datagram send/receive through the IP protocol conversation interface.

## Main Data Structures
- `Udp4hdr` and `Udp6hdr`: IPv4/IPv6 pseudo-header plus UDP header layouts used for checksum and packet construction.
- `Udpstats`: MIB-style datagram, no-port, error, and output counters.
- `Udppriv`: protocol-private hash table and stats.
- `Udpcb`: per-conversation state containing the `headers` mode flag.

## Behavior
- `udpinit` registers protocol `17` with connect, announce, create, close, receive, advise, ctl, state, and stats callbacks.
- `udpconnect` and `udpannounce` use standard Plan 9 connection setup and add the conversation to the protocol hash table.
- `udpcreate` opens a message receive queue and a bypass write queue that calls `udpkick` directly.
- `udpkick` builds IPv4 or IPv6 UDP packets, optionally consuming the Plan 9 `headers` address prefix, selecting a local address when needed, computing the pseudo-header checksum, and sending via `ipoput4` or `ipoput6`.
- `udpiput` validates IPv4 or IPv6 checksum, looks up the conversation, creates a new accepted conversation for announced non-header sockets, trims IP/UDP headers, optionally prepends source/local/interface/port metadata, and queues the datagram to `rq`.
- `udpadvise` maps ICMP-style advice back to matching conversations and hangs up queues unless advice is ignored.

## Control and Observability
- `headers` enables 52-byte address metadata on read/write.
- `udpstate` reports open/closed plus input/output queue lengths.
- `udpstats` reports in, no-port, error, and out datagram counters.

## Dependencies and Integration
Uses Plan 9 IP hash lookup, ICMP no-conversation responses, IPv6 host-unreachable responses, queue operations, block trimming/padding, local address selection, and protocol checksum helpers.

## Risks and Notes
IPv6 UDP checksums are always verified, while IPv4 checksum validation is conditional on a nonzero checksum field. Header mode lets users specify addresses per datagram, bypassing the connected peer fields for output.
