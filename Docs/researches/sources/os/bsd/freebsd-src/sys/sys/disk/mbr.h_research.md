# File Research: sources/os/bsd/freebsd-src/sys/sys/disk/mbr.h

## Purpose
Defines MBR layout constants, DOS partition type IDs, and the 16-byte MBR partition entry structure.

## Main Elements
- Offsets for boot sector, drive serial, partition table, magic, and partition entry size/count.
- Partition type constants for FAT, NTFS, extended, PReP, LDM, DragonFlyBSD, Linux, FreeBSD/386BSD, Apple, protective GPT, EFI, VMware, RAID.
- `struct dos_partition` stores CHS start/end, type, absolute start sector, and sector count.
- `DPSECT` and `DPCYL` decode CHS sector/cylinder fields.

## Dependencies And Integration
Used by MBR partition parsing and `sys/diskmbr.h`.

## Risk Notes
The size assertion fixes `struct dos_partition` at 16 bytes. CHS fields are legacy and should not be trusted for modern addressing when LBA fields exist.
