# File Research: sources/os/plan9/9front/sys/src/9/port/devsd.c

Purpose: Implements the generic storage device server `#S`, exposing storage controllers, units, partitions, control files, raw command files, and driver-added extra files.

Key logic:
- Registers `SDev` controller chains from `sdifc[]`, assigns device letters, lazily enables controllers, verifies units, and creates unit directories.
- Partitions are versioned `SDpart` entries; `sdinitpart` resets stale geometry, calls driver `online`, creates default `data`, and imports boot-configured `sdXpart=` partitions.
- Directory generation exposes top `sdctl`, unit `ctl`, exclusive `raw`, valid partition files, and extra driver files.
- `sdbio` maps partition byte I/O to sector-aligned driver `bio` calls, including bounds checks, removable-media locking, media-change retry, and read-modify-write for unaligned writes.
- `raw` implements a command/data/status state machine for SCSI CDBs and sneaky ATA commands.
- `sdrio`, `sdsetsense`, `sdfakescsi`, and `sdfakescsirw` provide raw command dispatch and SCSI emulation for non-SCSI devices.
- `sdwrite` handles top-level controller commands, legacy `config`, partition creation/deletion, unit driver controls, raw command phases, and partition writes.
- `sdconfig`, `configure`, `unconfigure`, `sdaddfile`, `sdshutdown`, and `sdannexctlr` manage dynamic controller lifetime and driver integration.

Dependencies and integration:
- Depends on `../port/sd.h`, driver callbacks in `SDifc`, `DevConf`, storage allocation helpers, and Plan 9 device/path conventions.

Risks and notes:
- Partition qid versions combine unit and partition versions, so stale opens fail with `Echange`.
- Raw command access is exclusive and stateful; incorrect phase ordering returns errors or resets the state.
- Dynamic unconfigure refuses busy controllers and must disable/clear hardware before freeing controller structures.
