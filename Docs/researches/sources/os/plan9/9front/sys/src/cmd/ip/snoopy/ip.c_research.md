# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ip.c

This module decodes IPv4 headers and demuxes by protocol number. The mux table contains many assigned IP protocol names, including ICMP, IGMP, TCP, UDP, IL, GRE, OSPF, and others.

Filters support source address, destination address, either address, and protocol number. `p_filter` validates the base header and advances by IHL.

`p_seprint` truncates the packet to the IPv4 total length when extra bytes are present, advances past the IPv4 header including options, and prints source, destination, id, fragment field, TTL, protocol, and length. It demuxes to the next protocol only for non-fragmented or first-fragment packets.
