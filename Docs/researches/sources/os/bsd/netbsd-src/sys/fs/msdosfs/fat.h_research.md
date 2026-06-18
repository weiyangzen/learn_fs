# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/fat.h

## Purpose
Defines FAT cluster constants, FAT type detection macros, EOF detection, FAT operation flags, extension flags, and FAT-manipulation prototypes.

## Main Contents
- Cluster constants for root/free cluster 0, first legal cluster 2, reserved/bad/EOF ranges, and end marker.
- FAT masks for FAT12, FAT16, and FAT32.
- `FAT12()`, `FAT16()`, and `FAT32()` classify a mounted filesystem using `pm_fatmask`.
- `MSDOSFSEOF()` tests whether a masked cluster value is in the EOF range.
- Defines `FAT_GET`, `FAT_SET`, and `FAT_GET_AND_SET` operation flags for `msdosfs_fatentry()`.
- Defines `DE_CLEAR` for zeroing newly allocated blocks.
- Declares cluster mapping, allocation, freeing, chain extension, FAT entry, FAT cache, in-use map, and free-chain functions.

## Dependencies
Requires `struct denode` and `struct msdosfsmount` declarations from surrounding msdosfs headers.

## Risks and Notes
EOF detection intentionally accepts the FAT range `0xfffffff8` through `0xffffffff` after masking. FAT type detection depends on mount-time `pm_fatmask` setup.
