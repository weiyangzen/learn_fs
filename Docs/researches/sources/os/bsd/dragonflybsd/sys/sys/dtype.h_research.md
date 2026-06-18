# File Research: sources/os/bsd/dragonflybsd/sys/sys/dtype.h

Legacy disk device type and filesystem type constants plus optional name tables.

Key responsibilities:
- Defines disk hardware/device type constants such as SMD, MSCP, SCSI, floppy, CCD, Vinum, and DiskOnChip.
- Under `DKTYPENAMES`, defines `dktypenames` and `DKMAXTYPES`.
- Defines partition filesystem type constants including unused, swap, historical UNIX/FFS/LFS/MSDOS/ISO9660, Vinum, RAID, CCD, HAMMER, HAMMER2, UDF, EFS, ZFS, NANDFS, encrypted, and unspecified.
- Under `DKTYPENAMES`, defines `fstypenames`, `fstype_to_vfsname`, and `FSMAXTYPES`.

Dependencies:
- Includes `sys/types.h`.
- Optional tables depend on `NELEM` being available from including context.

Notable risks:
- Numeric filesystem type values are on-disk label ABI and should not be reused casually.
- Some names map to NULL VFS names, so automount/probe code must tolerate unsupported legacy values.
