# File Research: sources/os/linux/linux/fs/squashfs/squashfs_fs.h

Defines SquashFS on-disk format constants, helper macros, and packed little-endian structures.

Includes magic/version assumptions, metadata block size, device block size selection, max file block size, name/count limits, filesystem flags, inode types, xattr namespace ids, compression ids, compressed-size decoding, and inode/fragment/id/xattr table indexing macros.

Defines meta-index cache structures used for large-file block-list acceleration.

Declares all on-disk structures: superblock, directory index/header/entry, base and extended inode variants, fragment entries, xattr entries/values/ids, and the xattr id table.
