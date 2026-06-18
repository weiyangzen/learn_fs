# File Research: sources/teaching/minix/minix/drivers/storage/at_wini/at_wini.h

## Purpose
Shared constants and declarations for the legacy AT/IDE driver and its live update module.

## Contents
- Includes MINIX driver, blockdriver, and driver-library headers.
- Defines ATA command/control/status register offsets for legacy I/O port access.
- Defines ATA command opcodes for read/write, LBA48, DMA, identify, flush, recalibrate, and specify.
- Defines identify-word offsets and masks for LBA, DMA, field validity, multiword DMA, UDMA, and LBA48.
- Defines bus-master DMA register offsets and flags.
- Defines ATAPI/SCSI packet command constants, phase bits, sense constants, packet sizes, and ATAPI identify command.
- Defines timeouts, retry counts, max sectors, minor counts, drive state flags, and boot variable `ata_no_dma`.
- Declares live update callbacks implemented in `liveupdate.c`.

## Integration Notes
The header mixes ATA and ATAPI constants because `at_wini.c` implements both protocols. It also exposes `w_command` indirectly through live update callback logic.

## Risks
Some constants are duplicated or overloaded for ATA and ATAPI status names. Any modification must account for both normal disk and ATAPI packet paths.
