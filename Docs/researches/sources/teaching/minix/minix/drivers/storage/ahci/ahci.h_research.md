# File Research: sources/teaching/minix/minix/drivers/storage/ahci/ahci.h

## Purpose
Defines AHCI, ATA, ATAPI, command table, HBA, port, timeout, state, flag, and minor-number constants used by `ahci.c`.

## Contents
- AHCI scale limits: `NR_PORTS`, `NR_CMDS`, `NR_PRDS`, memory layout sizes, command table alignment, and `MAX_TRANSFER`.
- Timeout defaults for spin-up, device detection, commands, I/O, and flushes.
- ATA FIS offsets, ATA commands, identify-word offsets, LBA48, DMA, NCQ, cache, FUA, and sector-size constants.
- ATAPI packet commands for readiness, sense, load/eject, capacity, read, and write.
- AHCI HBA and port register indexes and bit masks.
- Internal `cmd_fis_t` and PRD typedef.
- Device exposure constants copied from `at_wini`: 8 drives, normal partitions, subpartitions.
- Port-state enum, command-result enum, port flags, `NO_PORT`/`NO_DEVICE`, and verbosity levels.

## Integration Notes
The header is tightly coupled to `ahci.c`; no public API is exported beyond the driver. Its constants encode both hardware protocol and MINIX device-node compatibility.

## Risks
Incorrect register offsets or bit definitions directly affect hardware programming. `NR_PRDS` and `MAX_TRANSFER` must remain consistent with blockdriver I/O-vector limits and AHCI PRD constraints.
