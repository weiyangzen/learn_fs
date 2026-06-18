# File Research: sources/windows/reactos/sdk/lib/fslib/vfatxlib/fatx.c

Implements FATX formatting logic.

Key elements:
- Local `GetShiftCount` and `CalcVolumeSerialNumber` duplicate VFAT helper behavior.
- `FatxWriteBootSector` writes the 4096-byte FATX boot sector.
- `Fatx16WriteFAT` and `Fatx32WriteFAT` initialize a single FAT copy depending on cluster count.
- `FatxWriteRootDirectory` writes a root directory area filled with `0xff`.
- `FatxFormat` builds a FATX boot sector, uses 32 sectors per cluster, one FAT, computes cluster/FAT size, writes boot sector, FAT, and root directory.

Dependencies:
- Uses `vfatxlib.h` structures and `VfatxUpdateProgress`.
- Uses ReactOS NDK time/RTL APIs and `NtWriteFile`.

Research notes:
- FATX switches to 32-bit FAT entries when cluster count exceeds 65525.
- All on-disk positioning assumes 512-byte sectors plus a 4096-byte FATX boot sector.
- Full non-quick format is incomplete; it only contains a FIXME to fill remaining sectors.
