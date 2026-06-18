# File Research: sources/teaching/minix/minix/fs/ext2/open.c

This file implements creation of regular files, special nodes, directories, symlinks, and seek notifications.

Key entry points:
- `fs_create()`: creates a regular file and returns fsdriver node metadata.
- `fs_mknod()`: creates special files with device number stored in `i_block[0]`.
- `fs_mkdir()`: creates directory inode, then adds `.` and `..`, adjusting link counts.
- `fs_slink()`: creates symbolic links, using fast symlink storage when possible.
- `fs_seek()`: marks an inode as seeked to inhibit readahead.

Core helper:
- `new_node()`: allocates an inode, writes it before directory entry insertion for crash robustness, then creates the directory entry.

Important behavior:
- Directory creation rolls back the parent entry if `.` or `..` insertion fails.
- Symlink creation rejects targets larger than one block and rejects embedded NULs by comparing copied target length with `strlen`.
- On symlink failure, link count is cleared and the directory entry is deleted.

Dependencies:
- Uses `advance`, `alloc_inode`, `search_dir`, `rw_inode`, `new_block`, and `fsdriver_copyin`.
