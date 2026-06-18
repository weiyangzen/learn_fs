# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/fat.h

## Scope

Defines FAT cluster constants, FAT type predicates, EOF detection, FAT operation flags, and FAT allocation/traversal prototypes.

## APIs And Constants

- Defines root/free cluster aliases, first legal cluster, reserved, bad, and EOF cluster ranges.
- Defines masks for FAT12, FAT16, and FAT32 entries.
- `FAT12()`, `FAT16()`, and `FAT32()` inspect the mount fat mask.
- `MSDOSFSEOF()` tests whether a cluster is in the EOF range after applying the active FAT mask.
- Defines `FAT_GET`, `FAT_SET`, `FAT_GET_AND_SET`, and `DE_CLEAR`.
- Declares `pcbmap()`, cluster allocation/freeing, `fatentry()`, `freeclusterchain()`, `extendfile()`, FAT cache purge, and volume clean/dirty marking.

## Dependencies

Consumes `struct denode`, `struct msdosfsmount`, and `struct buf` from MSDOSFS and kernel headers.

## Risks And Invariants

FAT12/16/32 share higher-level cluster semantics but have different entry widths and masks. Callers must update denode file size and modified flags around `extendfile()` as documented.
