# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_address.h

## Purpose
Defines SCSI device addressing for SCSA target and HBA interaction, including legacy SPI addressing, complex unit-address mode, LUN conversion, and WWN string helpers.

## Main Interfaces
- `struct scsi_address`: HBA transport pointer plus SPI target/lun/sublun or complex `scsi_device` pointer.
- Legacy aliases: `a_target`, `a_lun`, `a_sublun`.
- Unit-address property names such as `target`, `lun`, `target-port`, `lun64`, `scsi-iport`, and SAS/SATA port properties.
- `scsi_lun64_t`, `scsi_lun_t`, and SCSI LUN addressing method constants.
- Kernel helpers for LUN conversion and WWN string conversion/freeing.

## Dependencies And Relationships
Includes `sys/scsi/scsi_types.h`. Closely tied to `transport.h` flags `SCSI_HBA_ADDR_SPI`, `SCSI_HBA_ADDR_COMPLEX`, and deprecated `SCSI_HBA_TRAN_CLONE`.

## Research Notes
The file contains important compatibility commentary: `scsi_address` is embedded at the base of `scsi_device` and copied into `scsi_pkt`, constraining structure evolution.

## Notable Risks
- Target drivers should not assume `a_target`/`a_lun` are valid outside SPI-style addressing.
- Unit-address representation is primarily HBA-owned; misuse can break non-SPI transports.
