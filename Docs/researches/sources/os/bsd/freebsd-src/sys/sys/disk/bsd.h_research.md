# File Research: sources/os/bsd/freebsd-src/sys/sys/disk/bsd.h

## Purpose
Defines the historical BSD disklabel on-disk structure, partition records, magic values, drive types, filesystem type codes, and disk flags.

## Main Elements
- `BSD_MAGIC`, min/max partition counts, bootblock size, raw and swap partition indices.
- `struct disklabel` stores geometry, hardware characteristics, flags, drive data, checksum, and partition table.
- `struct partition` stores size, offset, filesystem fragment details, filesystem type, and cylinders per group.
- Drive type constants include SCSI, ESDI, ST506, floppy, CCD, Vinum, RAID, JFS2.
- Filesystem type constants cover swap, FFS, MSDOS, LFS, ISO9660, boot, Vinum, RAID, ext2, NTFS, HAMMER/HAMMER2, UDF, ZFS, NANDFS.
- Disk flags include removable, ECC, bad-sector forwarding, RAM disk, and chained transfers.

## Dependencies And Integration
Included by `sys/disklabel.h` and partition/disklabel parsing code.

## Risk Notes
The structure is an on-disk ABI. The compile-time size assertion documents expected layout for the minimum partition count.
