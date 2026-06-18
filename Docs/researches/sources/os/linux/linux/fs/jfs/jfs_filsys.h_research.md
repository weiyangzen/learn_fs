# File Research: sources/os/linux/linux/fs/jfs/jfs_filsys.h

## Role

Defines JFS filesystem-wide constants, mount/superblock flags, fixed disk layout offsets, size limits, reserved inode numbers, and filesystem state values.

## Key Responsibilities

- Defines mount and aggregate flags for Unicode, error policy, quotas, no-integrity mode, discard, commit mode, inline log state, bad secondary AIT, sparse files, DASD limits, endian marker, directory index support, and OS/platform compatibility.
- Defines page, physical-block, dinode, inline-data, inode-extent, IAG, and filesystem block-size constants.
- Defines inode table geometry: 4096 inodes per IAG, 32 inodes per extent, 8 dinodes per 4 KiB page, and 512-byte on-disk dinodes.
- Defines min/max block sizes, maximum file size, maximum link count, minimum JFS partition size, and name/path limits.
- Provides block/byte conversion macros for physical/logical blocks and size-to-page/block calculations.
- Defines fixed physical block addresses and byte offsets for superblocks, aggregate inode map/table, secondary superblock, and block allocation map.
- Defines reserved front-of-aggregate space and aggregate inode table start.
- Defines aggregate reserved inode numbers and per-fileset reserved inode numbers.
- Defines superblock filesystem states such as clean, mounted, dirty, logredo failure, and extendfs-in-progress.

## Important Interactions

- Used by most JFS source files to interpret disk layout and feature flags.
- `JFS_DIR_INDEX` gates persistent directory cookie support in dtree code.
- Inode-map geometry constants are consumed by `jfs_imap.h` and `jfs_imap.c`.
- Fixed aggregate offsets are used by special inode read/write paths.
- State flags are used by mount/recovery/extendfs code outside this group.

## Invariants and Risks

- Constants encode on-disk format and cannot be changed without format incompatibility.
- Fixed physical-block macros are noted as legacy because underlying devices may not expose 512-byte physical sectors.
- `PSIZE` is fixed at 4096 and acts as the JFS buffer/metapage page size.
- `MAXFILESIZE` is `(1 << 52)`, not derived from VFS limits.
- Reserved inode numbers distinguish aggregate metadata inodes from fileset object inodes.
