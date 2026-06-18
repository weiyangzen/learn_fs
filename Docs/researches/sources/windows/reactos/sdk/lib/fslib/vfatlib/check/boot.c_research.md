# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/boot.c

This file reads, validates, reports, and lightly repairs FAT boot-sector metadata.

Core responsibilities:
- Parses FAT12/FAT16/FAT32 boot sector fields into `DOS_FS`.
- Computes logical sector size, cluster size, FAT start/size, root directory location, data area, cluster count, and FAT width.
- Validates accessible last sector, FAT size, root directory geometry, cluster count limits, and dirty state.
- Handles FAT32 backup boot sector comparison/repair and FSINFO creation/validation.
- Extracts volume label from boot-sector extended fields.
- Non-ReactOS code also supports writing labels into boot and root directory entries.

ReactOS-specific behavior:
- Uses `RtlStringCbPrintfA` in backup difference formatting.
- Dirty-bit auto-removal is gated by `rw`.
- Label-writing helpers are excluded under `__REACTOS__`.

Risk points:
- Many fatal boot-sector inconsistencies call `die`, which terminates the process in ReactOS adaptation.
- Interactive choices mostly collapse to auto/no-action paths depending on `interactive` and `rw`.
- FAT type detection is cluster-count based and warns rather than fixes some inconsistent FAT32 root directory layouts.
