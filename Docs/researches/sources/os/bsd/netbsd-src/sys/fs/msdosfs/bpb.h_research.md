# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/bpb.h

## Purpose
Defines BIOS Parameter Block structures and endian helpers for FAT12/FAT16/FAT32 boot-sector parsing.

## Main Contents
- Native `bpb33`, `bpb50`, and `bpb710` structs describe decoded DOS 3.3, DOS 5.0, and FAT32 BPBs.
- `byte_bpb33`, `byte_bpb50`, and `byte_bpb710` describe packed on-disk byte-array BPB layouts that avoid alignment assumptions.
- `getushort()`, `getulong()`, `putushort()`, and `putulong()` wrap little-endian decoding/encoding.
- `struct fsinfo` describes the FAT32 FSInfo sector, including signatures and free-cluster/next-free fields.
- Defines FAT32 extended flags such as active FAT number and mirroring, and the supported filesystem version.

## Dependencies
Includes `sys/endian.h`.

## Risks and Notes
The native BPB structs are useful after decoding, while the byte structs are safer for direct disk data. Callers must choose the right BPB version based on boot sector format and FAT type. Atari/GEMDOS support is documented but inactive.
