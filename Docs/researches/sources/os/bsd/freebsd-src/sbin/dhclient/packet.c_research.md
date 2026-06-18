# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/packet.c

## Purpose
Builds and validates raw Ethernet/IP/UDP packet headers for DHCP traffic.

## Main Elements
- `checksum()`: Internet checksum accumulator over byte buffers.
- `wrapsum()`: finalizes checksum into network order.
- `assemble_hw_header()`: writes broadcast Ethernet header with local source MAC when available.
- `assemble_udp_ip_header()`: builds IPv4 and UDP headers, including UDP pseudo-header checksum.
- `decode_hw_header()`: extracts Ethernet source hardware address and accounts for VLAN encapsulation.
- `decode_udp_ip_header()`: validates IP checksum, checks UDP payload length, accepts correct UDP checksums and a transmit-offload pseudo-header checksum case, and returns header length.

## Dependencies And Integration
Used by BPF send/receive paths for raw DHCP packets. Depends on protocol constants from `dhcpd.h` and system IP/UDP/Ethernet headers.

## Risk Notes
The checksum function casts buffer pairs to `u_int16_t *`, unlike `convert.c`; this assumes acceptable alignment in the buffers passed here. The decoder mutates `udp->uh_sum` while verifying.
