# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipv6.h

Defines IPv6 protocol constants, wire headers, and ICMPv6/ND interfaces.

Key definitions:
- Macros for multicast and link-local address tests, solicited-node multicast tests, and option-existence checks.
- Next-header values for IPv6 extension headers and common protocols.
- Multicast scope constants, prefix lengths, ICMPv6 unreachable codes, minimum IPv6 MTU, hop limit, and IPv6 header length.
- Neighbor discovery option types, including standard and Plan 9 extension values.
- Source/target mode constants for neighbor solicitation and local-target classifications.
- `IPV6HDR` packed header macro and `Ip6hdr`, `Opthdr`, `Routinghdr`, and `Fraghdr6` structures.
- Extern declarations for well-known IPv6 address arrays and prefix lengths.
- Prototypes for solicited-node multicast conversion and ICMPv6 neighbor/error send helpers.

Notable documentation:
- Header comments summarize relevant RFC lineage and note deprecated site-local addressing and routing-header type 0 risk.
