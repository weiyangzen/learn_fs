# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_fs.h

## Purpose
Canonical userspace copy of ext2/3/4 on-disk filesystem structures, constants, feature flags, and helper macros.

## Major Content
Defines:
- Reserved inode numbers including root, bad blocks, journal, resize, quota, snapshot/exclude, and replica inodes.
- Block, cluster, fragment, and group descriptor sizing macros.
- Old ext2 and ext4 group descriptors, including 64-bit block locations and checksum fields.
- Directory indexing structures: htree root info, dx entries, count/limit, and checksum tail.
- Inode flag constants, including extents, inline data, EA inode, encryption, verity, DAX, project inherit, and casefold.
- On-disk inode layouts:
  - `struct ext2_inode`
  - `struct ext2_inode_large`
- Superblock layout `struct ext2_super_block`, including ext4 fields for checksums, MMP, quotas, encryption, casefold, orphan file, high timestamps, and feature flags.
- Feature bits and generated inline feature accessors for compat, ro-compat, and incompat flags.
- Directory entry formats, directory checksum tail, file types, record-length calculation, and optional dirent hashes for encrypted+casefolded directories.
- MMP block format and sequence constants.
- Inline data and encoding constants.

## Integration
This header is included by `ext2fs.h`, `ext_attr.c`, `extent.c`, and nearly every metadata manipulation path. It bridges kernel ext-family disk format definitions into e2fsprogs.

## Risks and Notes
- Struct layout is disk ABI. Padding, field type, endian annotation, or offset changes are high risk.
- Feature test/set/clear helpers are used throughout the library to gate parsing and mutation behavior.
- Many macros have userland and kernel variants guarded by `__KERNEL__`.
