# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/bootsect.h

## Purpose
Defines on-disk FAT boot sector layouts for DOS 3.3, DOS 5.0, and DOS 7.10/FAT32 variants.

## Main Contents
- `struct bootsector33` models a 512-byte DOS 3.3 boot sector with 19-byte BPB, drive number, boot code, and 0x55/0xaa signature.
- `struct extboot` models the extended boot signature, volume ID, label, and FAT type string.
- `struct bootsector50` models DOS 5.0 with larger BPB and extension.
- `struct bootsector710` models FAT32-era boot sectors with 53-byte BPB and extension.
- `union bootsector` overlays the supported boot sector variants.
- Atari/GEMDOS commentary explains why no separate active structure is used.

## Dependencies
Uses fixed-width integer types supplied by including context.

## Risks and Notes
The structures assume 512-byte sector boot records and use byte arrays for BPB regions rather than parsed fields. Boot signature constants are defined in multiple struct scopes with the same macro names.
