# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ether.c

`snoopy` Ethernet decoder.

Key behavior:
- Parses Ethernet destination, source, and type.
- Filters on source, destination, either address, or EtherType.
- Demuxes to IPv4, ARP/RARP, IPv6, PPPoE discovery/session, EAPOL, AoE, and CEC.
- Formats source/destination/type/packet length.

Integration:
- Default root protocol for Ethernet packet capture and trace files.

Risks and notes:
- RARP maps to the same EtherType as ARP in this file, even though RARP commonly uses `0x8035`; may be historical or erroneous in this decoder.
