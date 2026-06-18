# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_defs.h

## Role

Shared SATA/ATA/SAT protocol definition header. It provides command opcodes, IDENTIFY data layout, SMART/log structures, ATAPI constants, NCQ constants, SCR bitfields, port-multiplier register definitions, and SCSI translation support constants.

## Key Elements

- Defines common ATA, ATAPI, SMART, SET FEATURES, queued I/O, port-multiplier, power-management, and microcode-download command/subcommand values.
- `sata_id_t` models ATA IDENTIFY DEVICE data across all 256 words, including serial, firmware, model, capabilities, command sets, SATA capabilities, sector sizing, WWN-ish fields, DSM/TRIM, SCT, rotation rate, and integrity word.
- Defines IDENTIFY word masks for ATA type, media/removable status, DMA/LBA support, command set support, SATA speed/NCQ support, write cache/read ahead, SMART, GPL, DSM/TRIM, SCT, and physical sector layout.
- Defines ATAPI type/signature/packet/DMA/interrupt-reason constants and default geometry/sector sizes.
- Defines NCQ and FIS constants.
- Defines ATA status, error, device-control, and device-head register bits.
- Defines SCSI/SAT support constants for log sense, self-test results, diagnostics, SMART mapping, SCSI ASC/ASCQ values, and device statistics logs.
- Defines packed-like protocol structures for NCQ error recovery log page, SMART data, SMART self-test logs, extended SMART self-test logs, read-log directory, log parameter, and acoustic management mode page.
- Defines port-multiplier GSCR/PSCR offsets and capability bits.
- Defines SStatus, SError, and SControl masks, shifts, values, and setter/getter macros, including SATA Gen3 and DevSleep-related IPM restrictions.

## Dependencies and Coupling

Included by both framework and HBA interface headers. It includes SCSI mode definitions and intentionally carries some SCSI constants that comments say should eventually live in generic SCSI headers.

## Research Notes

This header is protocol vocabulary rather than state. It spans older ATA/ATAPI compatibility through newer features such as Gen3 signaling, DSM/TRIM, SCT, device statistics, and extended SMART self-test logs.
