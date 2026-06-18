# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_smhba.h

## Purpose
Declares SM-HBA property names and helper routines for exposing PMCS HBA, iport, target, PHY, and device attributes.

## Main Interfaces
- Property string constants include number of PHYs, SM-HBA support, driver/hardware/firmware versions, supported protocol, manufacturer, serial number, and model name.
- `pmcs_smhba_add_hba_prop()`, `pmcs_smhba_add_iport_prop()`, and `pmcs_smhba_add_tgt_prop()` add individual typed properties.
- `pmcs_smhba_set_scsi_device_props()` and `pmcs_smhba_set_phy_props()` populate sets of SM-HBA properties.
- `pmcs_smhba_log_sysevent()` emits SM-HBA related sysevents.

## Dependencies And Relationships
Includes `sys/nvpair.h` for `data_type_t` and relies on PMCS HBA/iport/target/PHY types from the surrounding include chain.

## Research Notes
This is administrative/observability support rather than I/O-path logic.
