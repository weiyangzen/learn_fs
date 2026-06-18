# File Research: sources/os/linux/linux-stable/fs/romfs/internal.h

Private ROMFS header shared by storage, superblock, and NOMMU mmap code.

Key definitions:
- `struct romfs_inode_info`: embeds VFS inode and records metadata size plus file data offset from filesystem start.
- `romfs_maxsize(sb)`: returns filesystem image size stored in `sb->s_fs_info`.
- `ROMFS_I(inode)`: converts VFS inode to ROMFS inode info.

File-operation selection:
- Exposes `romfs_ro_fops` from `mmap-nommu.c` only for NOMMU + MTD builds.
- Otherwise maps `romfs_ro_fops` to `generic_ro_fops`.

Storage API:
- Declares `romfs_dev_read()`, `romfs_dev_strnlen()`, and `romfs_dev_strcmp()` for backing-store independent reads and directory-name handling.
