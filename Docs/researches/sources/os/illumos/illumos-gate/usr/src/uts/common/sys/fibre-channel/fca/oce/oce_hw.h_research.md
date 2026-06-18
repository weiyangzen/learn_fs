# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_hw.h

This packed hardware-interface header defines the Emulex OneConnect common register, doorbell, event, mailbox, and common-subsystem command formats used by the OCE driver.

Key contents:
- Device generation and device IDs for CNA Gen2/Gen3, TigerShark, and Tomcat.
- PCI/CSR register offsets for semaphores, soft reset, online status, interrupt control, POST state, and image transfer sizing.
- Doorbell offsets and bitfield unions for RX, TX, CQ, EQ, bootstrap mailbox, and MQ doorbells.
- Link-status, network-port, MAC-address-type, interface-capability, mailbox-ring-context, async-event, and RX-filter constants.
- Endian-aware bitfield unions for PCI config interrupt control, semaphores, soft reset, online status, MPU semaphore/control, and hardware doorbells.
- Event queue entry `oce_eqe`, mailbox scatter/gather entry `oce_mq_sge`, mailbox payload `oce_mbx_payload`, mailbox envelope `oce_mbx`, MQ CQE `oce_mq_cqe`, async link-state CQE, and bootstrap mailbox `oce_bmbx`.
- Mailbox subsystem and common-opcode enumerations for interface MAC operations, link status, flash access, queue creation/destruction, flow control, firmware config, VLAN config, RX filter config, MSI message changes, function reset, and function link config.
- Common mailbox request/response header `mbx_hdr` plus status helper macros.
- Mailbox payload structures for link query/set, MAC query/set/add/delete, multicast table, VLAN tags, interface create/destroy, EQ/CQ/MQ context creation/destruction, firmware version, flow control, flash read/write, firmware configuration, VLAN configuration, RX filters, EQ delay modification, maximum mailbox buffer query, function reset, and link enable/disable.

Dependencies:
- Includes `sys/types.h`.
- Uses packed structs and extensive `_BIG_ENDIAN` conditional bitfields.

Research notes:
- This is an ABI-sensitive device wire-format header. Structure layout, packing, endian fields, page-array limits, and opcode values must match firmware.
- Queue creation commands expose hardware context formats for EQ, CQ, and MQ rings, while `oce_io.h` wraps them in driver queue objects.
- Filesystem relevance is indirect through storage/network driver infrastructure: this is a high-speed NIC/FCoE-era hardware contract in the illumos kernel tree.
