# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_var.h

## Purpose
Primary private header for the LSI/Avago/Broadcom MPT SAS HBA driver. It defines driver-wide constants, DMA/SGL limits, target/enclosure/RAID state, command tracking, hotplug topology records, per-PHY SM-HBA data, the main `mptsas_t` soft state, register/queue helper macros, debug hooks, and prototypes for the MPT SAS implementation.

## Main Interfaces
- `mptsas_target_t`, `mptsas_smp_t`, and `mptsas_enclosure_t` model SSP/STP targets, SMP expanders, and enclosure metadata.
- `mptsas_cmd_t` wraps `scsi_pkt` state with DMA cookies, SGL state, ARQ/extra-sense buffers, active-slot metadata, timeout flags, and a target pointer.
- `mptsas_slots_t` tracks outstanding commands by SMID, reserving slot zero and a final task-management slot.
- `mptsas_t` is the central HBA instance state: SCSA/SMP transports, mutexes/CVs, target refhashes, RAID config, active/wait/done queues, DMA frame regions, interrupts, firmware/diagnostic buffers, SAS PHY info, dynamic reconfiguration taskq state, UFM handle, and IOC capability flags.
- Macros cover MPI request-frame sizing, SG element sizing for MPI 2.5/IEEE SGE formats, queue removal, register doorbell access, interrupt masking, target/LUN extraction, and LUN validity checks.
- Prototypes expose command save/remove, polling, DMA allocation, firmware update/check/download, IOC reset/init, configuration page access, RAID operations, topology/PHY discovery helpers, FMA checks, and SM-HBA stats.

## Dependencies And Relationships
Includes illumos DDI/SCSI/MDI support plus MPI2 tool/config headers. It is consumed by the MPT SAS driver implementation files for transport, IOC setup, config-page traversal, RAID support, passthrough, firmware diagnostics, and hotplug event handling.

## Research Notes
The header is mostly driver state and protocol plumbing. The key design point is that normal I/O, event-ack, passthrough/config, firmware, and task-management commands all share a single command/slot framework but use distinct flags and synchronization paths.
