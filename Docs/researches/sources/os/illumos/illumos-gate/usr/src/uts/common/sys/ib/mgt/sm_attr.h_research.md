# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/sm_attr.h

This header defines InfiniBand Subnet Management attributes from IB spec volume 1, release 1.1, chapter 14. It is a wire-layout and constants header for SMP/MAD subnet management.

Key definitions:
- `SM_MAX_DR_PATH` is 64.
- SMP class headers: `sm_lid_class_hdr_t`, `sm_dr_mad_hdr_t`, `sm_dr_class_hdr_t`, `sm_dr_data_t`.
- Directed-route status/direction bits: `SM_DR_SMP_D_OUT`, `SM_DR_SMP_D_IN`, `SM_DR_SMP_D_MASK`, `SM_DR_SMP_STATUS_MASK`.
- Trap numbers for GID service changes, multicast GID creation/destruction, link state, threshold events, capability/sysimage changes, bad M_Key/P_Key/Q_Key, and switch P_Key violations.

Trap payloads:
- `sm_trap_64_t` shared with traps 65/66/67.
- `sm_trap_128_t`, `sm_trap_129_t` shared with 130/131, `sm_trap_144_t`, `sm_trap_145_t`.
- `sm_trap_256_t`, `sm_trap_257_t` shared with 258, and `sm_trap_259_t` include endian-sensitive bitfields.

Subnet management attribute layouts:
- `sm_nodedesc_t`, `sm_nodeinfo_t`, `sm_switchinfo_t`, `sm_guidinfo_t`, `sm_portinfo_t`, `sm_pkey_table_t`, `sm_pkey_block_element_t`, `sm_SLtoVL_mapping_table_t`, `sm_VL_weight_block_t`, `sm_VLarb_table_t`, `sm_linear_forwarding_table_t`, `sm_lid_port_block_t`, `sm_random_forwarding_table_t`, `sm_multicast_forwarding_table_t`, `sm_sminfo_t`, `sm_vendor_diag_t`, `sm_ledinfo_t`.

Constants:
- Node types: CA, switch, router.
- Switch partition/raw-filter enforcement masks.
- Port capability mask bits including SM, notice/trap, reset/APM, NVRAM keys, LED info, CM/SNMP/DM/VM, DR notice, boot management, and client reregistration.
- Port state, physical state, link widths/speeds, M_Key protection levels, MTU values, VL capabilities, operational VLs, partition enforcement, forwarding table sizing, SM state and SMInfo action modifiers.
- Attribute IDs for SM MADs.

Layout/portability notes:
- Many structures use `_BIT_FIELDS_HTOL`/`_BIT_FIELDS_LTOH` conditional definitions for exact wire bit ordering.
- This file is included by SA record definitions and is a foundational InfiniBand management ABI header.

Dependencies:
- Includes `sys/ib/ib_types.h` and `sys/ib/mgt/ib_mad.h`.

Relevance:
- Supports kernel InfiniBand fabric management; relevant to storage transports such as iSER/RDMA even though it is not filesystem code.
