# File Research: sources/os/linux/linux/fs/ext2/namei.c

Read status: complete, 434 lines.

This file implements ext2 VFS namespace operations. It is the glue between VFS inode operations and the directory record helpers in `dir.c`.

Key responsibilities:
- Lookup names with `ext2_lookup()`.
- Return parent dentries for export/reconnect paths with `ext2_get_parent()`.
- Create regular files, tmpfiles, device/special nodes, symlinks, hard links, directories, unlink, rmdir, and rename.
- Expose directory and special-file inode operation tables.

Operation flow:
- `ext2_lookup()` validates name length, resolves inode number via `ext2_inode_by_name()`, loads inode through `ext2_iget()`, and returns `d_splice_alias()`.
- `ext2_create()` allocates a new inode, installs regular file ops, marks it dirty, and adds the directory link.
- `ext2_tmpfile()` creates an unlinked regular file and finishes simple open.
- `ext2_mknod()` creates special files and installs `ext2_special_inode_operations`.
- `ext2_symlink()` uses fast symlinks when the target fits in `i_data`, otherwise writes a slow symlink through page-cache data.
- `ext2_link()` increments and instantiates hard links.
- `ext2_mkdir()` increments parent link count, creates child directory inode, initializes `.`/`..`, and links it into parent.
- `ext2_unlink()` deletes the directory entry and decrements target link count.
- `ext2_rmdir()` verifies emptiness, unlinks, zeroes size, and decrements directory link counts.
- `ext2_rename()` supports `RENAME_NOREPLACE`, handles replacement, directory parent `..` updates, link counts, ctime updates, and old-entry deletion.

Error handling and consistency:
- Name length over `EXT2_NAME_LEN` returns `-ENAMETOOLONG`.
- Lookup of a deleted inode referenced by a directory entry reports filesystem error and returns `-EIO`.
- New inode failure paths decrement link counts and discard new inodes.
- Directory rename validates target emptiness when replacing directories.
- Quotas are initialized on directories before namespace mutations.

External dependencies:
- Relies on `dir.c` for directory layout operations.
- Relies on `ialloc.c` for inode allocation.
- Relies on `inode.c` for inode loading and operation setup.
- Exposes hooks for xattrs, ACLs, file attributes, getattr, and setattr.

Research notes:
- The file intentionally avoids directory layout details; it orchestrates VFS semantics and link-count correctness.
- It is the main user-visible namespace mutation path for ext2.
