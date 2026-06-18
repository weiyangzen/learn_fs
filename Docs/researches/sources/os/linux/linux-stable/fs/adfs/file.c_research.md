# File Research: sources/os/linux/linux-stable/fs/adfs/file.c
- Purpose: Defines ADFS regular-file VFS operation tables.
- Main exports: `adfs_file_operations` and `adfs_file_inode_operations`.
- File ops: Uses generic read/write/mmap/splice/llseek helpers appropriate for buffered filesystem files.
- Inode ops: Wires `adfs_setattr` for metadata changes.
- Integration: Actual block mapping and writeback are implemented in `inode.c`; this file supplies the VFS table glue.
