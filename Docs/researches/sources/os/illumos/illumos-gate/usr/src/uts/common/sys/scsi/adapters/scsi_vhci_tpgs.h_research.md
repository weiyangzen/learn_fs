# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/scsi_vhci_tpgs.h

## Purpose
Defines TPGS-specific constants and a helper prototype for SCSI VHCI target-port-group failover support.

## Main Interfaces
- Retry constant `STD_FO_MAX_CMD_RETRIES` for standard failover polling when transport errors or rejected commands occur.
- TPGS access states include active optimized, active non-optimized, standby, unavailable, and transitioning.
- Sense ASC/ASCQ constants identify state transition, state changed, invalid parameter list, invalid command opcode, and target-port accessibility states.
- `vhci_tpgs_get_target_fo_mode()` reports target failover mode, state, extended logical failover capability, and preferred status for a `scsi_device`.

## Dependencies And Relationships
Used by the TPGS failover module and VHCI failover logic to interpret ALUA/TPGS access states and sense data.

## Research Notes
This is a small policy/protocol companion header for the broader failover ABI in `scsi_vhci.h`.
