# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ether.c

This module decodes Ethernet II headers and demuxes by ethertype. It maps IPv4, ARP, RARP, IPv6, PPPoE discovery/session, EAPOL, AoE, CEC, and VLAN ethertypes.

Filters support source, destination, either address, and type. Protocol-name filters compile to type comparisons and set the next protocol.

`p_seprint` validates the 14-byte header, consumes it, demuxes by ethertype, and prints source address, destination address, protocol type, and total frame length.

Notable detail: both ARP and RARP entries use ethertype `0x0806`; RARP normally uses a distinct ethertype, so this table may classify RARP only by explicit filter behavior rather than wire ethertype accuracy.
