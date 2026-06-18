# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/bpb.h

## Scope

Defines BIOS Parameter Block and FAT32 FSInfo layouts plus endian helpers for FAT filesystems.

## Data Structures And Constants

- `bpb33`, `bpb50`, and `bpb710` describe host-aligned BPB variants for DOS 3.3, DOS 5.0, and FAT32.
- `byte_bpb33`, `byte_bpb50`, and `byte_bpb710` describe on-disk byte-array versions to avoid compiler alignment issues.
- Defines FAT32 extended flags `FATNUM`, `FATMIRROR`, filesystem version `FSVERS`, root cluster, FSInfo sector, backup sector, and reserved fields.
- `struct fsinfo` describes FAT32 free-count/next-free metadata and signatures.
- Defines `getushort`, `getulong`, `putushort`, and `putulong` as little-endian decode/encode helpers.

## Dependencies

Includes `<sys/types.h>` and `<sys/endian.h>`.

## Risks And Invariants

On-disk BPB data must use byte layouts and little-endian helpers. FAT32 mount validation depends on interpreting fields such as FAT size, mirroring flags, root cluster, and FSInfo correctly.
