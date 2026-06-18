# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/arp.c

This module decodes ARP and RARP packets. It uses the same parser and printer for both `Proto arp` and `Proto rarp`.

Fields support IPv4 source protocol address, target protocol address, either protocol address, hardware source, hardware target, and either hardware address. `p_filter` validates minimum ARP length, advances past the header, and compares fields using protocol or hardware address lengths from the packet.

`p_seprint` prints operation, protocol/hardware address lengths, source protocol/hardware addresses, and target protocol/hardware addresses. It is a leaf protocol.
