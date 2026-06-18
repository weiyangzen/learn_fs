# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/ata8-acs.h

## Purpose
Provides a compact subset of ATA8-ACS command opcodes needed by the PMCS SATA path.

## Main Interfaces
- `enum ata_opcode` maps ATA command names to opcode bytes, including reads/writes, DMA/queued/FPDMA variants, SMART, IDENTIFY, PACKET, SET FEATURES, cache flush, security commands, native max address, trusted commands, logs, and power-management commands.

## Dependencies And Relationships
Included by `ata.h` and used when building SATA host I/O FIS payloads in the PMCS driver.

## Research Notes
This header is declarative and intentionally limited to command constants. It contains a duplicate value for trusted send variants as written in the source.
