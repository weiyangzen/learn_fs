# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/common.c

Provides shared helpers for FAT12/FAT16/FAT32 formatting.

Key elements:
- `GetShiftCount` computes a shift value for power-of-two division, used to avoid 64-bit division.
- `CalcVolumeSerialNumber` derives a FAT volume serial from current system time fields.
- `FatWipeSectors` zero-fills the target volume in cluster-sized chunks and reports progress.

Dependencies:
- Uses ReactOS NDK time and file APIs through `vfatlib.h`.
- Calls `UpdateProgress` from `vfatlib.c`.
- Allocates through the process heap.

Research notes:
- `FatWipeSectors` allocates one cluster-sized zero buffer, then handles any trailing sectors after whole-cluster writes.
- `GetShiftCount` assumes power-of-two inputs for correct sector-size and cluster-size division use.
