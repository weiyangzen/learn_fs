# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_hw.h

## Purpose
Defines the Hermon hardware ABI: PCI IDs, page/register constants, firmware command register layout, command mailbox structures, endian-specific hardware bitfields, queue/context formats, event/completion entry extraction macros, WQE segment formats/builders, UAR/doorbell layouts, FCoIB/ethernet structures, performance counters, and flash register constants.

## Main Interfaces
- PCI and base hardware constants:
  - Mellanox vendor/device IDs for SDR, DDR, DDR Gen2, QDR Gen2, QDR Gen2V, and maintenance mode.
  - Native 4 KiB page constants.
  - Command BAR offsets for HCR, software reset, and semaphore.
- `struct hermon_hw_hcr_s`: HCA command register fields with masks/shifts for token, status, go, event, toggle, opmod, and opcode.
- Query/init command layouts:
  - `hermon_hw_querydevlim_s`
  - `hermon_hw_queryfw_s`
  - `hermon_hw_queryadapter_s`
  - `hermon_hw_vpm_s`
  - `hermon_hw_initqueryhca_s`
  - helper parameter structures for QP/CQ/EQ/RDB, multicast, TPT, UAR, and QP allocation.
- Port and ethernet configuration:
  - `hermon_hw_query_port_s`
  - `hermon_hw_set_port_s`
  - ethernet set-port variants for general parameters, receive QPN calculation, MAC table, VLAN table, priority table, and GID table.
  - `hermon_hw_conf_int_mod_s`
- Memory and translation:
  - `hermon_hw_dmpt_s`, `hermon_hw_cmpt_s`, `hermon_hw_mtt_s`
  - MPT/MTT ownership, region/window, physical-address, and present flags.
- Event and completion:
  - `hermon_hw_eqc_s`, EQ status/state constants.
  - EQE payload variants for CQ, QP, CQ error, port state, GPIO, command completion, operational error, page fault, and FCoIB error.
  - `hermon_hw_eqe_s` union and extraction macros.
  - `hermon_hw_cqc_s`, CQ status/state constants.
  - `hermon_hw_cqe_s` and extraction macros for QPN, immediate/PKey/credit, DQPN, GRH, path bits, DLID, SL, byte count, WQE counter, error syndrome, opcode, send/receive, checksum/IPoIB status, and FEXCH fields.
- Queue contexts:
  - `hermon_hw_srqc_s`
  - `hermon_hw_mod_stat_cfg_s`
  - `hermon_hw_msg_in_mod_s`
  - `hermon_hw_udav_s`, `hermon_hw_udav_enet_s`
  - `hermon_hw_addr_path_s`
  - `hermon_hw_rss_s`
  - `hermon_hw_qpc_s`
  - QP state/service constants for RC, UC, UD, FCMND, FEXCH, XRC, MLX, and RFCI.
- Multicast/FCoIB/counters:
  - `hermon_hw_mcg_s`, `hermon_hw_mcg_en_s`, `hermon_hw_mcg_qp_list_s`
  - `hermon_hw_set_mcast_fltr_s`
  - `hermon_hw_config_fc_basic_s`
  - `hermon_hw_query_fc_s`
  - `hermon_hw_arm_req_s`
  - `hermon_hw_sm_perfcntr_s`, `hermon_hw_sm_extperfcntr_s`
- UAR, doorbells, and WQEs:
  - `hermon_hw_send_db_reg_t`, `hermon_hw_cq_db_reg_t`, `hermon_hw_guest_eq_ci_t`, `struct hermon_hw_uar_s`
  - `hermon_hw_qp_db_t`, `hermon_hw_cq_db_t`
  - Send, SRQ, FCP3, UD, bind, LSO, remote address, atomic, local invalidate, FRWR, MLX, and SGL segment structures.
  - WQE builder macros for UD, LSO, RDMA remote address, RC atomic, atomic, bind, FRWR, local invalidate, FCP3 init, receive/send data segments, inline segments, control segments, MLX LRH/GRH/BTH/DETH.
- Flash:
  - PCI config offsets, CR-space flash offsets, GPIO/semaphore constants, SPI opcodes/registers, masks, and timeouts.

## Dependencies And Relationships
This is the central hardware contract used by command posting, resource allocation, QP/CQ/EQ/SRQ/MR setup, multicast handling, FCoIB, ioctl flash access, and statistics. Other headers mostly define software handles and prototypes around these hardware structures.

## Research Notes
The file maintains separate little-endian and big-endian bitfield definitions for most hardware mailbox/context structures. Several hot-path macros avoid bitfield writes and instead build network-ordered 32/64-bit chunks with producer memory barriers.
