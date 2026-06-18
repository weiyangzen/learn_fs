# File Research: sources/os/linux/linux/fs/romfs/super.c

ROMFS superblock, inode, directory, page-cache read, mount, and module lifecycle implementation for block-backed and MTD-backed ROMFS images.

Key functions include `romfs_read_folio()`, `romfs_readdir()`, `romfs_lookup()`, `romfs_iget()`, `romfs_fill_super()`, `romfs_get_tree()`, `romfs_kill_sb()`, and module init/exit registration. The file maps ROMFS on-disk file header types to Linux inode modes and directory entry dtypes.

Mount validation reads the first 512 bytes, checks ROMFS magic words, image size, MTD bounds, and checksum, then computes the root inode offset from the volume name length. The filesystem is forced read-only and no-atime; reconfigure also forces `SB_RDONLY`.

Directory traversal follows ROMFS linked file headers through `ri.next`, uses `romfs_dev_*` helpers from `internal.h`, handles hard-link entries by switching inode number/source offset to `ri.spec`, and emits dentries through VFS helpers.

Notable invariants: inode number is the ROMFS image offset, data offset is metadata size aligned by `ROMFH_MASK`, and all reads must stay below `romfs_maxsize()`. Error paths generally return `-EIO`, `-EINVAL`, or allocation failures; `romfs_readdir()` suppresses device-read errors by returning `0` after `goto out`.
