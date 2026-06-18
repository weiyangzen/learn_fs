# File Research: sources/os/plan9/9front/sys/src/9/ip/ipv6.h

Defines IPv6 constants, header layouts, address predicates, and ICMPv6 helper prototypes.

Key elements:
- Defines multicast/link-local/ULA tests.
- Lists IPv6 next-header values and neighbor-discovery option constants.
- Defines IPv6 minimum MTU, base header size, and fragment header size.
- Declares `Ip6hdr`, `Opthdr`, `Routinghdr`, and `Fraghdr6`.
- Exposes common IPv6 multicast, loopback, link-local, and mask globals.
- Declares ICMPv6 neighbor solicitation/advertisement and error routines.

Dependencies:
- Included by IPv6, TCP, UDP, and interface code that needs IPv6 protocol metadata.

Research notes:
- Routing header type 0 is explicitly flagged as dangerous in comments.
- IPv4-mapped address handling is implemented elsewhere, but this file defines shared IPv6 wire layout.
