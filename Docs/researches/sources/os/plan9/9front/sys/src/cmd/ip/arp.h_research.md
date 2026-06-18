# File Research: sources/os/plan9/9front/sys/src/cmd/ip/arp.h

Defines ARP packet, cache entry, stats structures, and constants.

Key points:
- `Arppkt` describes Ethernet ARP/RARP wire format, including Ethernet header, hardware/protocol types, lengths, op, sender/target hardware addresses, and sender/target IPv4 addresses.
- `ARPSIZE` is 42 bytes.
- `Arpentry` maps Ethernet address to IPv4 address for user-level ARP interactions.
- `Arpstats` tracks hits, misses, and failures.
- Defines Ethernet type constants for ARP/RARP and operation constants for ARP/RARP request/reply.

Dependencies and interactions:
- Comment notes use by kernel, `arpd`, `snoopy`, and `tboot`.

Research relevance:
- Shared protocol definition header for ARP-related Plan 9 networking components.
