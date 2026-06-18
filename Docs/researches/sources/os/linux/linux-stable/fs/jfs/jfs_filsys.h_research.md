# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_filsys.h

This header defines implementation-wide JFS filesystem constants: mount flags, fixed sizes, reserved on-disk locations, reserved inode numbers, name limits, and filesystem state bits.

Key responsibilities:
- Defines mount/superblock flags for Unicode names, error handling policy, quotas, no-integrity mode, discard/TRIM, commit behavior, inline logs, sparse files, DASD limits, endian flags, directory indexing, and platform compatibility.
- Defines fixed JFS geometry constants such as page size, physical block size, disk inode size, inline inode data size, inline xattr size, inode allocation group size, inode extent size, and min/max filesystem block sizes.
- Defines conversion helpers for logical/physical block numbers and byte sizes to page/block numbers.
- Defines fixed physical block and byte offsets for the primary superblock, aggregate inode map, aggregate inode table, secondary superblock, and block allocation map.
- Defines reserved aggregate and fileset inode numbers, including aggregate metadata inodes, the fileset inode map, root inode, ACL inode, and first regular object inode.
- Defines directory/path length limits and superblock state values such as clean, mounted, dirty, logredo failure, and extendfs in progress.

Important interactions:
- Included throughout JFS to keep on-disk layout assumptions consistent across superblock, inode map, block map, dtree, and xtree code.
- Constants such as `INOSPERIAG`, `INOSPEREXT`, `DISIZE`, `IDATASIZE`, and `PSIZE` are directly used by inode map and directory code.
- Mount flags such as `JFS_DIR_INDEX`, `JFS_OS2`, and `JFS_BAD_SAIT` materially change behavior in dtree, imap, and mount/recovery paths.

Notable invariants and risks:
- Several offsets are fixed JFS on-disk ABI; changing them would break existing filesystems.
- JFS assumes a 4096-byte metadata page size while allowing filesystem logical block sizes from 512 to 4096 bytes.
- Reserved inode numbers are overloaded between aggregate-level and fileset-level namespaces and must be interpreted in the correct context.

Research notes:
- This file is the shared geometry and feature-flag contract for the rest of the JFS implementation.
