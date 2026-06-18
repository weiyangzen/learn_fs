# File Research: sources/os/plan9/plan9/sys/src/9/ip/icmp6.c

Implements ICMPv6, including neighbor discovery support.

Key responsibilities:
- Registers protocol `icmpv6` for next-header 58.
- Creates read/write queues and supports a `headers` ctl mode where user data supplies explicit IPv6 source/destination addresses.
- Computes ICMPv6 checksums by temporarily treating the IPv6 header as a pseudoheader.
- Sends echo replies, neighbor solicitations, neighbor advertisements, host unreachable, TTL exceeded, and packet-too-big messages.
- `valid` verifies ICMPv6 length/checksum and applies RFC 2461-style checks for neighbor solicit/advert, router solicit/advert, hop limit, code, target address, and option lengths.
- `icmpiput6` dispatches echo requests, unreachable/time-exceeded advice, router solicit/advert delivery, neighbor solicitation responses, duplicate-address-discovery-relevant neighbor advertisements, packet-too-big, and default queued delivery.
- Integrates with ARP/ND cache via `arpenter` for IPv6 neighbor entries.
- `icmpstats6` reports aggregate and per-type counters.

Notable behavior:
- Neighbor solicitation for tentative local addresses is treated specially for duplicate address detection.
- Link-local and multicast-specific validation is enforced for ND control messages.
