# File Research: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs.h

## Summary
Defines Squashfs on-disk constants, encoding helpers, metadata/table macros, meta-index structures, compression ids, and all on-disk structure layouts.

## Main Contents
- Filesystem version, metadata size, max block/file/name sizes, invalid sentinels, and flags.
- Compression and uncompressed-block encoding macros.
- Inode-number, fragment, inode lookup, id, and xattr table offset macros.
- Meta-index cache constants and structures.
- On-disk little-endian superblock, inode variants, directory entries, fragments, and xattr structures.

## Important Behavior
`squashfs_block_size()` rejects block-list values with high reserved bits set. Table macros convert logical indices into metadata block numbers and offsets for packed compressed tables.

Inode variants are optimized by type and size: short and long forms exist for regular files, directories, symlinks, devices, and IPC nodes when larger values or xattrs are required.

## Risks
This header is the exact on-disk format contract. Any interpretation bug propagates into mount validation, inode parsing, directory lookup, xattr handling, and export filehandle lookup.
