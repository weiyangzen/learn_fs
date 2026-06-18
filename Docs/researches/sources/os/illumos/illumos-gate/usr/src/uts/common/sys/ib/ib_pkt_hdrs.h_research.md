# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ib_pkt_hdrs.h

This core IB header defines wire-layout structs and masks for InfiniBand packet headers.

Core definitions:
- `ib_lrh_hdr_t` models the Local Route Header with VL/version, service level/next header, DLID, packet length, and SLID.
- LRH masks extract virtual lane, link version, service level, next-header type, and packet length; next-header values include raw, IPv6, BTH, and GRH.
- `ib_grh_t` models the Global Route Header with IP version/traffic class/flow label, payload length, next header, hop limit, SGID, and DGID.
- GRH masks extract IP version, traffic class, flow label, and BTH next-header value.
- `ib_bth_hdr_t` models Base Transport Header fields: opcode, solicited/migration/pad/version byte, P_Key, destination QP, ACK/PSN.
- BTH masks extract solicited event, migration request, pad count, transport version, destination QP, ACK request, and PSN.
- `ib_deth_hdr_t` models Datagram Extended Transport Header Q_Key and source QP.

Risk-sensitive invariants:
- These structs describe on-wire IB headers; consumers must handle endian conversion externally as needed.
- QP and PSN fields are 24-bit values masked from 32-bit fields.
- `IB_DETH_SRC_QP_MASK` is defined twice with the same value.
