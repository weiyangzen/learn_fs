# File Research: sources/os/linux/linux-stable/fs/ext2/namei.c

## Summary
Implements ext2 VFS namespace operations: lookup, create, tmpfile, mknod, symlink, link, mkdir, unlink, rmdir, rename, parent lookup, and operation tables.

## Main Responsibilities
- Bridges VFS inode operations to ext2 inode allocation and directory-entry helpers.
- Resolves dentries through linear directory lookup.
- Creates regular files, special files, symlinks, directories, hard links, and tmpfiles.
- Removes directory entries and adjusts link counts.
- Renames entries, including directory `..` updates across parents.
- Provides exportfs parent lookup through `ext2_get_parent()`.

## Key APIs
- `ext2_dir_inode_operations`.
- `ext2_special_inode_operations`.
- `ext2_get_parent()`.

## Important Behavior
Create/mknod/link/mkdir/unlink/rename initialize quotas for affected directories. `ext2_add_nondir()` centralizes link insertion and new inode instantiation; on failure it drops link count and discards the new inode.

Symlinks are stored as fast symlinks in `i_data` when they fit, otherwise as pagecache-backed slow symlinks. `mkdir` increments parent and child link counts, writes `.` and `..`, then adds the directory entry. `rename` supports only `RENAME_NOREPLACE`, handles replacement link counts, checks non-empty target directories, and updates `..` when moving a directory across parents.

## Risks
Correct link-count rollback is critical in create, mkdir, symlink failure, hardlink failure, unlink, rmdir, and rename paths. Directory layout manipulation is delegated to `dir.c`, so these operations depend on mapped folio release and directory-entry update correctness there.
