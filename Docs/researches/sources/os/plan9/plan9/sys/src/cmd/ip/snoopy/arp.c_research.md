# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/arp.c

`snoopy` ARP/RARP decoder.

Key behavior:
- Parses standard Ethernet/IPv4 ARP fields.
- Filters on source/target protocol address or hardware address.
- Formats opcode, protocol/hardware lengths, protocol addresses, and Ethernet addresses.
- Defines both `Proto arp` and `Proto rarp` using the same implementation.

Integration:
- Reached from Ethernet demux for ARP and RARP placeholder.

Risks and notes:
- Hardware-address comparisons use packet `hln` as comparison length, so malformed large `hln` can over-read filter address storage conceptually.
