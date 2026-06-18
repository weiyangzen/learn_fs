# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/transport.h

## Purpose
Defines the SCSA HBA transport interface: `scsi_hba_tran`, HBA attach/allocation APIs, packet allocation helpers, initiator-port and target-map interfaces, and minor-number conventions.

## Main Interfaces
- `scsi_hba_tran_t` and `struct scsi_hba_tran`: HBA vector table for target init/probe/free, packet start, reset, abort, capability, packet allocation, DMA lifecycle, reset notify, event callbacks, quiesce, bus reset/config/power, packet setup/teardown, FMA, iport, and target map state.
- HBA lifecycle functions: `scsi_hba_init`, `scsi_hba_fini`, `scsi_hba_attach_setup`, `scsi_hba_detach`, `scsi_hba_tran_alloc`, `scsi_hba_tran_free`.
- Packet helpers: `scsi_hba_pkt_alloc`, `scsi_hba_pkt_free`, `scsi_hba_pkt_comp`.
- Discovery/topology helpers for iports and target maps.
- Flags: `SCSI_HBA_TRAN_*`, `SCSI_HBA_ADDR_SPI`, `SCSI_HBA_ADDR_COMPLEX`, `SCSI_HBA_HBA`, `SCSI_HBA_SCSA_*`.

## Dependencies And Relationships
Kernel-only header relying on DDI/SCSA types, `sys/modctl.h`, `sys/note.h`, and types declared through `scsi_types.h` consumers. It is referenced by `scsi_address.h`, `scsi_resource.h`, and HBA drivers.

## Research Notes
The file documents the transition from legacy SPI addressing and deprecated `SCSI_HBA_TRAN_CLONE` to `SCSI_HBA_ADDR_COMPLEX` and iport/target-map based topology.

## Notable Risks
- `struct scsi_hba_tran` is a kernel ABI-like contract for HBA drivers; field misuse can break packet routing, DMA setup, hotplug, FMA, or MPxIO behavior.
- Minor-node macros reserve framework ranges; HBA private minors must avoid collisions.
- Target-map callbacks can activate/deactivate devices asynchronously, so locking and lifetime ownership matter.
