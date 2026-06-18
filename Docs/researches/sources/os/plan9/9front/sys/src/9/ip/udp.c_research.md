# File Research: sources/os/plan9/9front/sys/src/9/ip/udp.c

Implements UDP for IPv4 and IPv6.

Key elements:
- Defines IPv4 and IPv6 UDP pseudo-header layouts.
- Implements connect/announce/create/close and per-conversation source IP tracking.
- Builds outbound IPv4 or IPv6 UDP packets, computes checksums, and sends through IP output.
- Supports `headers` mode, where user data includes remote/local/interface addresses and ports.
- Validates inbound checksums, performs hash lookup, creates accepted conversations for announced endpoints, trims packet headers, and queues payloads.
- Emits ICMP no-conversation errors for unmatched datagrams.
- Supports transparent forwarding/NAT translation and ICMP advice/proxy advice.
- Provides MIB-style UDP stats.

Dependencies:
- Uses `Fsstdconnect`, `Fsstdannounce`, `Fsnewcall`, IP hash tables, IPv4/IPv6 output, ICMP, and translation helpers.

Research notes:
- IPv6 UDP checksum is mandatory here; IPv4 allows a zero checksum.
- For multicast/broadcast receives, the accepted conversation stores a unicast source IP for replies.
