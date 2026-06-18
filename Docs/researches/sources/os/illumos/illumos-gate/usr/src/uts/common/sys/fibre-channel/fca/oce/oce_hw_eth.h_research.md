# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_hw_eth.h

This header defines the OCE NIC-subsystem hardware descriptors, mailbox commands, statistics layouts, and RSS configuration used for Ethernet transmit and receive operation.

Key contents:
- NIC WQE size, packet type constants, header/data split modes, and WQ type constants.
- NIC mailbox opcodes for RSS, ACPI, promiscuous mode, stats, WQ/RQ create/delete, RSS CQ, RSS MSI, HDS RQ, and advanced RSS.
- RSS enable flags for IPv4, TCP/IPv4, IPv6, and TCP/IPv6 hashing.
- Packed transmit descriptor formats:
  - `oce_nic_hdr_wqe` for header WQEs with checksum, LSO, VLAN, event, completion, total length, and MSS fields.
  - `oce_nic_frag_wqe` for fragment physical address and length.
  - `oce_nic_tx_cqe` for TX completion status, WQE index, packet count, WQ ID, LSO/cast encoding, and valid bit.
- Receive descriptor formats:
  - `oce_nic_rqe` for RX fragment address.
  - `oce_nic_rx_cqe` for packet size, VLAN tag, fragment index/count, checksum pass flags, packet type, RSS data, HDS metadata, and valid bit.
- Valid/invalidate macros for TX and RX CQEs.
- Mailbox payloads for promiscuous mode, NIC WQ create/delete, NIC RQ create/delete, NIC stats retrieval, and RSS configuration.
- Hardware statistics structs:
  - `rx_port_stats`
  - `rx_stats`
  - `tx_counter`
  - `tx_stats`
  - `rx_err_stats`
  - `mem_stats`
  - `mbx_get_nic_stats`

Dependencies:
- Includes `oce_hw.h`.
- Shares packed and endian-sensitive wire formats with firmware and hardware queues.

Research notes:
- This is the Ethernet-specific half of the OCE hardware contract, complementing the common mailbox/register definitions in `oce_hw.h`.
- The stat layout feeds `oce_stat.h` and the driver's kstats.
- RX/TX CQE valid-bit handling and descriptor invalidation are central to queue-drain correctness.
