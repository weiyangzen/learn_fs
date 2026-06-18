# File Research: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang.h

`iplang.h` defines data structures shared by the IP language lexer/parser.

Key structures:
- `iface_t`: named interface with MTU, IPv4 address, Ethernet address, next pointer, and opened device fd.
- `send_t`: selected interface plus gateway address for sending.
- `arp_t`: IPv4-to-Ethernet ARP mapping list entry.
- `aniphdr_t`: linked nested header descriptor used while building packets. It stores a union pointer to IP/data/TCP/UDP/ICMP data, option length, last option, protocol, header length, and next/previous links.

It also defines convenience aliases (`ah_ip`, `ah_data`, `ah_tcp`, `ah_udp`, `ah_icmp`) and declares `get_arpipv4()`.

This header is the structural backbone for `iplang_y.y` packet construction.
