# File Research: sources/os/linux/linux/fs/hpfs/namei.c

Purpose: Implements HPFS namespace mutation operations: create, mkdir, mknod, symlink, unlink, rmdir, symlink read, and rename.

Key functions:
- `hpfs_update_directory_times()` updates directory mtime/ctime and writes metadata.
- `hpfs_mkdir()` allocates an fnode and root dnode, creates the `^A^A` self entry, inserts a directory dirent, initializes the inode, and updates parent link count/times.
- `hpfs_create()` allocates an fnode and regular-file dirent, initializes file inode/page-cache ops, and writes ownership/mode EAs if needed.
- `hpfs_mknod()` creates special files only when writable EAs are enabled, storing mode/device metadata through inode writeback.
- `hpfs_symlink()` creates symlinks only when writable EAs are enabled, storing target text in the `SYMLINK` EA.
- `hpfs_unlink()` removes non-directory dirents and drops the inode link.
- `hpfs_rmdir()` verifies a directory is empty by counting dnode items, removes its dirent, and clears link counts.
- `hpfs_symlink_read_folio()` reads symlink target data from the `SYMLINK` EA.
- `hpfs_rename()` supports `RENAME_NOREPLACE`, rejects directory overwrite, moves/replaces dirents, updates parent directory accounting, and updates the moved fnode’s parent/name fields.
- `hpfs_dir_iops` wires directory inode operations.

Dependencies and integration:
- Uses allocation, dnode insertion/removal, EA handling, inode writeback, symlink address-space ops, and global HPFS locking.

Risk notes:
- Special files and symlinks depend on EA write support (`sb_eas >= 2`).
- Rename over an existing directory is rejected even if empty.
- Namespace operations must carefully unwind allocated fnodes/dnodes on failure to avoid leaks or corruption.
