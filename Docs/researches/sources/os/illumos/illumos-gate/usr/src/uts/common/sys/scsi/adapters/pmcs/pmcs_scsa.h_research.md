# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_scsa.h

## Purpose
Defines the PMCS interface to the illumos SCSA midlayer, including address/packet conversion macros, the PMCS command wrapper, status sizing, wait-queue return codes, and SCSA-facing prototypes.

## Main Interfaces
- Macros map SCSI addresses, transport structures, packets, and PMCS command wrappers to HBA/iport/target-private state.
- `pmcs_cmd_t` wraps a `scsi_pkt` with queue linkage, DMA chunk list, target/LUN pointers, firmware tag, and SATL tag.
- Prototypes cover SCSA initialization, status latching, residual setting, wait/completion queue running, target/LUN configuration, SMP child discovery/configuration, and SATA special command handling.

## Dependencies And Relationships
Included by `pmcs.h`; depends on `pmcs_hw_t`, `pmcs_cmd_t`, `pmcs_xscsi_t`, `pmcs_lun_t`, and `pmcs_dmachunk_t`. It links the PMCS firmware queueing layer to illumos target-driver packet flow.

## Research Notes
The header separates normal command flow from SATA special queue handling, matching the target flags in `pmcs_xscsi_t`.
