# sources/test-tools/strace/bundled/linux/include/uapi/linux/packet_diag.h

## Purpose

Defines netlink diagnostic ABI structures for packet sockets. strace uses this to decode `SOCK_DIAG_BY_FAMILY` requests for `AF_PACKET` sockets and their optional multicast list, ring, fanout, memory, and filter attributes.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. `struct packet_diag_req` carries family, protocol, inode, show-mask, and cookie filters. `PACKET_SHOW_INFO`, `PACKET_SHOW_MCLIST`, `PACKET_SHOW_RING_CFG`, `PACKET_SHOW_FANOUT`, `PACKET_SHOW_MEMINFO`, and `PACKET_SHOW_FILTER` select response details. `struct packet_diag_msg` is the base response. Attribute ids are `PACKET_DIAG_INFO`, `PACKET_DIAG_MCLIST`, `PACKET_DIAG_RX_RING`, `PACKET_DIAG_TX_RING`, `PACKET_DIAG_FANOUT`, `PACKET_DIAG_UID`, `PACKET_DIAG_MEMINFO`, and `PACKET_DIAG_FILTER`. Payload structs include `packet_diag_info`, `packet_diag_mclist`, and `packet_diag_ring`.

## Control Flow, State, and Integration

No functions are defined. The control pattern is netlink request selection followed by a kernel diagnostic dump of packet socket state. Persistent state belongs to live packet sockets: ring sizing, membership addresses, fanout group, socket flags, UID, and filters.

## Risks and Test Signals

Risks are attribute-number drift, incorrectly sizing the fixed 32-byte hardware address array, and treating diagnostic output as portable across kernel versions without checking requested show bits. Test signals include netlink decoder coverage for every `PACKET_SHOW_*` flag, ring field formatting, `PDI_*` flags, and graceful display of missing optional attributes.
