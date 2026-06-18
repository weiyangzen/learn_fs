# File Research: sources/teaching/minix/minix/drivers/storage/filter/inc.h

## Purpose
Common include and shared declaration header for the filter driver.

## Contents
- Pulls in MINIX system, IPC, partition, DS, blockdriver, optset, and libc headers.
- Defines `SECTOR_SIZE`.
- Defines checksum modes: `ST_NIL`, `ST_XOR`, `ST_CRC`, `ST_MD5`.
- Defines disk operation modes: `FLT_WRITE`, `FLT_READ`, `FLT_READ2`.
- Defines `struct driverinfo` for backing-driver label, minor, endpoint, up-event state, problem state, error, retry, and kill counters.
- Defines DS up-event states, `RET_REDO`, backing-driver problem states, driver indexes, buffer sizes, label size, and `sector_t`.
- Declares global configuration variables from `main.c`.
- Declares cross-module functions from `sum.c`, `driver.c`, and `util.c`.

## Integration Notes
This is the central coupling point for all filter source files. Runtime configuration is shared as mutable globals.

## Risks
Because it declares global mutable configuration and cross-layer APIs, changes can affect all filter layers. `SECTOR_SIZE` is fixed at 512 and assumed throughout layout math.
