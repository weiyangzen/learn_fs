# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/boot.c

## Purpose

Parses and validates the FAT boot sector and FAT32 FSInfo sector into the internal `struct bootblock`.

## Main Entry Points

- `readboot(int dosfs, struct bootblock *boot)`: reads BPB/EBPB fields, validates geometry/layout, computes derived FAT layout values.
- `writefsinfo(int dosfs, struct bootblock *boot)`: updates FAT32 FSInfo free-count and next-free hints.

## Key Checks

- Boot signature must be `0x55aa`.
- Sector size must be 512 through 4096 and a power of two.
- Sectors per cluster must be nonzero and a power of two.
- Reserved sectors and FAT count must be valid.
- FAT32 must use 32-bit total-sector and FAT-sector fields, not legacy 16-bit fields.
- EXFAT OEM name is rejected.
- FAT32 version must be 0.0.
- FSInfo signatures are validated and optionally repaired.
- FAT type is inferred from cluster count, with bounds checks for FAT12/16/32.
- FAT size must fit the computed cluster count.

## Derived Fields

Computes `NumSectors`, `FATsecs`, `FirstCluster`, `NumClusters`, `ClustMask`, `NumFatEntries`, `ClusterSize`, and initial statistics counters.

## Integration Points

Feeds `readfat()` and directory traversal with trusted layout. Uses `ask()`, `pfatal()`, `pwarn()`, and `perr()` from the fsck utility layer.

## Risk Notes

All later FAT offsets depend on this file’s arithmetic. It contains overflow and bounds checks for FAT count, sectors per FAT, cluster area position, and FAT entry capacity.
