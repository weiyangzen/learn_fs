# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/bootsect.h

## Scope

Defines on-disk FAT boot sector layouts for DOS 3.3, DOS 5.0, and DOS 7.10/FAT32 style media.

## Data Structures And Constants

- `struct bootsector33`, `bootsector50`, and `bootsector710` represent 512-byte boot sectors with jump, OEM name, BPB byte area, optional extension, boot code padding, and trailing signature bytes.
- `struct extboot` defines the extended boot signature, volume ID, volume label, and filesystem type fields.
- `union bootsector` provides a common overlay.
- Defines boot-sector signatures `BOOTSIG0` and `BOOTSIG1`, and extended signatures `EXBOOTSIG` and `EXBOOTSIG2`.

## Dependencies

Uses fixed-width integer types and is consumed by mount/boot-sector parsing code outside this grouped file list.

## Risks And Invariants

The fields are byte arrays where alignment matters; callers must parse embedded BPB regions with matching BPB structures and endian helpers.
