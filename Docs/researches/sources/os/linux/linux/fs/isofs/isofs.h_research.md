# File Research: sources/os/linux/linux/fs/isofs/isofs.h

Private ISOFS header defining in-memory inode/superblock structures, endian-number helpers, prototypes, and inode numbering helpers.

Key structures:
- `struct iso_inode_info`: ISOFS private inode fields for iget block/offset, first extent, file format, compression parameters, multi-section continuation, section size, and embedded VFS inode.
- `struct isofs_sb_info`: mount-wide ISOFS state including zones, first data zone, logical zone size, Rock Ridge/Joliet/mapping/check/session flags, permission overrides, uid/gid, NLS table, and behavior flags.

Helpers:
- `ISOFS_SB()` and `ISOFS_I()` cast VFS objects to ISOFS private structures.
- `isonum_711/712/721/722/723/731/732/733()` decode ISO 711/721/733-style numeric fields. The dual-endian 723/733 helpers intentionally trust little-endian due to broken mastering programs.
- `isofs_get_ino()` derives stable 32-bit inode numbers from metadata block/offset.
- `isofs_normalize_block_and_offset()` normalizes directory identities to their `.` record.

Prototypes connect inode, directory, Rock Ridge, Joliet, lookup, block mapping, export, symlink, and file attribute operations.
