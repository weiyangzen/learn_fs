# File Research: sources/teaching/minix/minix/fs/mfs/open.c

`open.c` implements node creation operations: regular files, device nodes, directories, symbolic links, and seek notification. All creation paths route through the private `new_node` helper.

`fs_create` creates a regular node in a parent directory and returns an `fsdriver_node` with inode metadata. `fs_mknod` creates special nodes, storing the device number in zone zero. `fs_mkdir` creates the directory inode, then inserts `.` and `..`; if either insertion fails, it removes the parent directory entry and undoes the initial link count. It increments the parent link count for the new `..`.

`fs_slink` creates a symlink inode, allocates the first block, copies the user-provided link target, appends a NUL byte, rejects targets that fill the block or contain embedded NULs, and cleans up the inode/directory entry on failure.

`new_node` rejects deleted parents and directory link-count overflow, checks whether the final component already exists, allocates a fresh inode, increments its link count, writes it to disk before inserting the directory entry for crash robustness, and frees it again if directory insertion fails. `fs_seek` marks an inode as recently seeked to suppress aggressive read-ahead.
