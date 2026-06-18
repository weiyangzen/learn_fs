# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/parts.c

This file reads disk partition tables during early boot, especially for bootstrap kernels that do not use newer `9load` partition discovery.

Key responsibilities:
- Wraps an `SDunit` as `PSDunit` with opened `ctl` and `data` channels.
- `psdaddpart` updates both the in-memory `SDunit` partition table and the underlying `devsd` control file.
- `psdread` and `sdreadblk` read bounded sectors from a partition.
- `oldp9part` parses legacy Plan 9 ASCII partition tables near the end of disk.
- `mbrpart` parses DOS MBR partitions, including DMDDO offset handling, extended partitions, first DOS partition naming, and Plan 9 partition discovery.
- `p9part` parses newer Plan 9 partition tables inside a named partition.
- `part9660` detects ISO9660 boot media and creates a `9fat` partition for `bootdisk.img`.
- `rdgeom`, `setpartitions`, and `readparts` open `/ctl` and `/data` files, read geometry, and populate partition state.
- `sdaddconf` serializes discovered partitions into boot configuration for the next kernel.

Important implementation details:
- Partition parsing is intentionally early-boot and channel-based, not a full disk management stack.
- Sector size defaults to 512 but can be overridden by geometry; ISO9660 expects `Cdsec`.
- The code guards partition bounds when reading through `psdread`.
- New MBR/Plan 9 partition parsing is preferred unless `partition=old` is configured.

Filesystem/storage relevance:
- Directly supports early access to disk-backed filesystems and NVRAM/factotum paths by making partitions visible before the normal user startup scripts run.
