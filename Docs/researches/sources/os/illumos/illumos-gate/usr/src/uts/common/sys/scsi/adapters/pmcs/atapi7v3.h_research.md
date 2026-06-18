# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/atapi7v3.h

## Purpose
Defines the SATA Frame Information Structure formats from ATA/ATAPI-7 used by the PMCS SATA command path.

## Main Interfaces
- FIS structures include host-to-device register FIS, device-to-host register FIS, set-device-bits FIS, DMA activate/setup FIS, BIST activate FIS, PIO setup FIS, and a generic bidirectional FIS.
- FIS type constants cover `FIS_REG_H2DEV`, `FIS_REG_D2H`, `FIS_SET_DEVICE_BITS`, `FIS_DMA_ACTIVATE`, `FIS_DMA_FPSETUP`, `FIS_BIST_ACTIVATE`, `FIS_PIO_SETUP`, and `FIS_BI`.
- IDC bit constants define command, interrupt, and data indicators.
- `fis_t` reserves five dwords for common FIS payloads used by PMCS helper routines.

## Dependencies And Relationships
Included by `ata.h`; consumed by PMCS SATA command building, FIS dumping, identify, and special-command handling.

## Research Notes
The comments explicitly document 28-bit and 48-bit ATA field mapping into the host-to-device register FIS, which is useful when reviewing PMCS SATA translation code.
