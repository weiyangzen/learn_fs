# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_satl.h

## Role

Small SATL/SAT-2 support header for SCSI ATA PASS THROUGH translation.

## Key Elements

- Includes SPC-3 SCSI type definitions.
- Defines ATA PASS THROUGH protocol field values for hardware reset, software reset, non-data, PIO data-in/out, DMA, DMA queued, diagnostics, device reset, UDMA in/out, FPDMA, and return-response-info.
- Defines bit masks for ATA PASS THROUGH EXTEND, CK_COND, T_DIR, and BYTE_BLOCK bits.

## Dependencies and Coupling

Used by SATL translation code in the SATA framework. It is protocol-constant-only and has no state structures.

## Research Notes

This header narrows in on SAT ATA PASS THROUGH CDB interpretation; broader ATA command and status constants live in `sata_defs.h`.
