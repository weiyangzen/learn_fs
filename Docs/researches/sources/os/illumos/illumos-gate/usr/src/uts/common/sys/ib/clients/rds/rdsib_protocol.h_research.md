# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_protocol.h

This legacy RDS-over-IB wire-protocol header defines versioning, default sizing, CM private data, data headers, and control packets.

Core definitions:
- RDS version is 4 and service ID is Sun-OUI-based `0x1000144F00000001`.
- Defaults include max nodes, 4K user data buffer size, per-session send/receive buffer counts, receive low-water marks, and pending RX high-water percentage.
- `RDS_THIS_ARCH` permits only homogeneous Solaris architecture interoperability across sparcv9, amd64, and i386.
- `rds_cm_private_data_t` carries IBT IP CM private data, version, architecture, endpoint type, failover flag, last buffer ID, user buffer size, ACK rkey, and ACK address.
- `rds_data_hdr_t` carries buffer ID, payload length, packet count, packet sequence number, source port, and destination port.
- Control packet codes cover stall, unstall, all-ports stall/unstall, heartbeat, and close session.
- `rds_ctrl_pkt_t` carries port and control code.

Risk-sensitive invariants:
- Wire structs contain native-width pointer-sized fields; the header explicitly limits interoperability to homogeneous Solaris architectures.
- Packet segmentation relies on `dh_npkts` and `dh_psn`.
- Failover recovery depends on private-data last buffer IDs and ACK memory registration.
