# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cfg.h

## Role

`tavor_cfg.h` defines the Tavor configuration profile structure and initialization hooks. The profile captures hardware resource sizing, queue capabilities, memory-mapping policy, port limits, agent policy, and GUID overrides used during attach and HCA initialization.

## Major Definitions

The header defines the fixed hardware port count (`TAVOR_NUM_PORTS`) and supported DDR sizing constants for 256 MB, 128 MB, and a minimal profile.

`tavor_cfg_profile_t` is the main configuration object. It contains:
- QP, CQ, SRQ, EQ, RDB, MCG, MPT, MTT, mailbox, UAR, PD, AH, PKey, and GID sizing fields.
- WQE SGL limits and real maximum SGL values.
- SRQ/FMR enablement fields and FMR remap limits.
- Multicast hash and QP-per-group parameters.
- HCA RDMA responder/initiator limits, MTU, port width, VL capability, and port count.
- Firmware-vs-software QP0/QP1 management-agent policy.
- DMA mapping policy, consistent-sync override, IOMMU bypass, and streaming-disable-on-bypass behavior.
- Work-queue placement policy for QP/SRQ queues.
- Reset and command polling delays.
- ACK request, split transaction, and read burst defaults.
- MSI preference.
- optional system image, node, and port GUID overrides.

## Interfaces

The file declares two-phase configuration profile initialization and profile finalization.

## Integration Notes

The profile is consumed by resource initialization, HCA initialization mailbox construction, queue allocation, DMA synchronization decisions, and port setup. Many fields can be controlled by driver configuration variables but must remain within hardware-reported limits.
