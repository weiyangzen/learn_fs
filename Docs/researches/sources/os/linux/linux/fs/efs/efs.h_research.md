# File Research: sources/os/linux/linux/fs/efs/efs.h

Defines EFS on-disk structures, in-memory inode private state, constants, and internal APIs.

Key behavior:
- Sets EFS block size to 512 bytes.
- Defines extent format, device encoding, 128-byte disk inode layout, directory entries, directory block layout, slot macros, and maximum name length.
- Defines `struct efs_inode_info` with direct extents, extent counts, last extent cache, and embedded VFS inode.
- Provides `INODE_INFO()` and `SUPER_INFO()` container helpers.
- Declares directory, symlink, inode, lookup, export, block mapping, and bmap interfaces.

Important interactions:
- Shared by all EFS implementation files.
- The extent structure is stored on disk in packed byte form and converted manually in `inode.c`.
