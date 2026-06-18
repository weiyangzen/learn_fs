# File Research: sources/local-fs/jfsutils/include/jfs_filsys.h

Defines JFS filesystem-wide constants, flags, fixed offsets, reserved inode numbers, and states.

Key contents:
- Superblock platform/feature flags: AIX, OS/2, DFS, Linux, Unicode, commit modes, inline log, bad secondary AIT, sparse files, DASD, directory index.
- Fundamental sizes: 4096-byte page, 512-byte physical block, 512-byte inode, inode extent/page/IAG sizes, min/max block size, max file size, link max, minimum JFS partition size.
- Fixed physical block and byte offsets for primary superblock, aggregate inode map/table, secondary superblock, and block map.
- Reserved aggregate inode numbers: aggregate inode map, block map, inline log, bad block inode, fileset inode.
- Reserved fileset inode numbers: root, ACL, extension, first object.
- Directory path/name limits.
- Filesystem state flags: clean, mounted, dirty, logredo failed, extendfs in progress.

Interactions:
- Used throughout JFS utilities for validating and constructing on-disk layouts.
- `extract.c` validates superblock flags and offsets using these constants.

Research notes:
- Defines both legacy physical-block constants and preferred byte-offset constants, with comments noting physical-block macros should be removed.
