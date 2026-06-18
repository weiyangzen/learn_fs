# File Research: sources/os/bsd/dragonflybsd/sys/sys/disklabel32.h

Legacy BSD 32-bit sector-based disklabel on-disk format and ioctl ABI.

Key responsibilities:
- Defines label sector/offset for i386/x86_64 boot use, magic number, partition count, raw/swap/label partition indexes.
- Defines `struct disklabel32` with magic, drive type/subtype, type/pack names, geometry, spare/alternate cylinder data, hardware timing/skew fields, drive data, checksum, partition count, boot/superblock sizes, and fixed partition table.
- Defines `struct partition32` with sector count, sector offset, filesystem block/fragment metadata, filesystem type, and cpg/sgs union.
- Implements inline `dkcksum32()` XOR checksum over label through active partitions.
- Declares kernel `disklabel32_ops`.
- Defines ioctls to get, set, write, and get virgin 32-bit labels.

Dependencies:
- Includes types, optional kernel systm, and ioccom.
- Depends on disklabel ops declared by `disklabel.h` when used with abstraction.

Notable risks:
- Sector counts and offsets are 32-bit, limiting large-disk representation.
- Checksum depends on `d_npartitions`; invalid values can affect checksum scan bounds unless validated before use.
