# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/sdbios.c

This file adapts BIOS disk devices into the Plan 9 `sd` storage interface for read-only bootstrap use.

Key responsibilities:
- Exposes `sdbiosifc`, an `SDifc` named `"bios"`.
- `biospnp` creates an `SDev` for BIOS devices after BIOS initialization.
- `biosonline` populates sector size and sector count using BIOS helper functions.
- `biosrio` handles selected SCSI disk commands over BIOS reads, including extended read and capacity queries.
- Rejects writes because boot programs do not write through BIOS disks.
- Provides big-endian packing helpers for SCSI capacity responses.

Filesystem/storage relevance:
- Lets bootstrap code use standard `sd` partition and block interfaces over BIOS-backed disks.
- Read-only design reduces risk during early boot but limits recovery/write scenarios.
