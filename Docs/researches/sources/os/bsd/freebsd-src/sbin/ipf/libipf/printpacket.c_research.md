# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpacket.c

Packet summary/hex printer for test traffic.

Key behavior:
- Computes IPv4 or IPv6 packet length and asserts it matches `msgdsize()`.
- `OPT_HEX` dumps raw mbuf-chain bytes.
- IPv6 packets are delegated to `printpacket6()`.
- IPv4 summary prints direction, interface, ID, length/header length, protocol, fragment offset, endpoints, ports, and TCP flags.

Research notes:
- Assumes transport header is present for non-fragmented TCP/UDP summaries.
