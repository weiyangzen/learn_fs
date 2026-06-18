# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_mbufdebug.c

This file provides read-only packet decoders for inspecting mbuf chains in debug contexts. Its public entry point is `m_examine(const struct mbuf *, int af, const char *modif, void (*pr)(...))`, which dispatches by address family to hex, Ethernet, ARP, IPv4, or IPv6 decoders.

The utility layer avoids modifying mbuf chains. `m_peek_data()` copies arbitrary byte ranges out of a possibly fragmented chain, and `m_peek_len()` decides whether to inspect only the current mbuf (`modif` contains `c`), the packet-header length, or the sum of chain lengths. Address/protocol formatting helpers render Ethernet, IPv4, IPv6, and IP protocol names.

Protocol decoders are layered in packet order. `m_examine_ether()` prints MAC addresses, handles VLAN tags by advancing to the encapsulated ethertype, and dispatches to PPPoE, ARP, IPv4, or IPv6. PPPoE and PPP support common discovery/session fields and then dispatch to IP decoders where possible. ARP prints hardware/protocol types, operation, and Ethernet/IPv4 sender/target addresses when the format is parseable.

`m_examine_ip()` prints IPv4 header fields, flags, checksum, source/destination addresses, and dispatches to ICMP/TCP/UDP. `m_examine_ip6()` prints IPv6 version/flow/payload/next-header/hop-limit/address fields, strips one Hop-by-Hop header, and dispatches to ICMPv6/TCP/UDP. ICMP/ICMPv6 print known message type names. TCP prints ports, sequence/ack, flags, window/checksum/urgent pointer, and parses common options: MSS, window scale, SACK permitted, and timestamps. UDP prints ports and length. `m_examine_hex()` prints at most 128 remaining bytes in four-byte columns.

The file is intentionally diagnostic rather than validation-grade: many unknown or short cases fall back to hex output. Risks are bounded by debug use, but parser assumptions are visible, including fixed header reads, limited IPv6 extension handling, static formatting buffers, and a PPPoE tag loop that should be treated cautiously if adapted outside debug output.
