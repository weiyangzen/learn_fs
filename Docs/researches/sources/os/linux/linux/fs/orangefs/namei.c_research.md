# File Research: sources/os/linux/linux/fs/orangefs/namei.c

Implements OrangeFS directory inode operations for namespace changes.

Key behavior:
- `orangefs_create()` sends `ORANGEFS_VFS_OP_CREATE`, creates a local inode from returned ref, instantiates the dentry, sets dentry timeout, and updates parent mtime/ctime.
- `orangefs_lookup()` sends `ORANGEFS_VFS_OP_LOOKUP`, returns `NULL` inode for `ENOENT`, otherwise uses `orangefs_iget()` and `d_splice_alias()`.
- `orangefs_unlink()` sends `ORANGEFS_VFS_OP_REMOVE`, drops inode link count, and updates parent times; also used for `rmdir`.
- `orangefs_symlink()` validates target length, sends `ORANGEFS_VFS_OP_SYMLINK`, creates a symlink inode, sets symlink size locally, and updates parent times.
- `orangefs_mkdir()` sends `ORANGEFS_VFS_OP_MKDIR`, creates a directory inode, instantiates dentry, and keeps directory nlink effectively constant due to multi-client consistency limits.
- `orangefs_rename()` rejects nonzero rename flags, updates destination parent times, sends `ORANGEFS_VFS_OP_RENAME`, and updates overwritten dentry ctime.

Important exported table:
- `orangefs_dir_inode_operations` wires lookup, ACLs, create, unlink, symlink, mkdir, rmdir, rename, setattr/getattr, xattr listing, permission, and update_time.
