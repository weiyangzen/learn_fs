# File Research: sources/os/linux/linux-stable/fs/minix/namei.c

## Purpose

Implements MINIX directory inode operations for lookup, create, mknod, tmpfile, symlink, hardlink, mkdir, unlink, rmdir, and rename.

## Main Entry Points

- `minix_lookup()`: resolves a directory entry name to an inode.
- `minix_create()` / `minix_mknod()` / `minix_tmpfile()`: create regular, special, or unnamed temporary files.
- `minix_symlink()`: creates a page-cache-backed symlink.
- `minix_link()`: creates a hardlink to an existing inode.
- `minix_mkdir()` / `minix_rmdir()`: create and remove directories with link-count updates.
- `minix_unlink()`: removes a non-directory entry.
- `minix_rename()`: renames or replaces entries, including directory `..` updates.
- `minix_dir_inode_operations`: exports the operation table to VFS.

## Control Flow And State

Creation allocates a new MINIX inode, assigns inode operations with `minix_set_inode()`, marks it dirty, and inserts the directory entry through `minix_add_link()`. `add_nondir()` centralizes the instantiate-or-drop path and decrements the new inode link count on insertion failure.

`mkdir()` increments the parent link count, initializes the child as a directory, increments the child link count for `.` and `..`, fills the empty directory, and links it into the parent. Failure unwinds both child and parent link counts. `unlink()` finds the directory entry, deletes it, updates the victim ctime from the directory, and decrements its link count. `rmdir()` checks parent link count sanity, verifies the target is empty, calls unlink, and decrements parent and child directory counts.

`rename()` supports only `RENAME_NOREPLACE`. It finds the old entry and, for directory renames, the child `..` entry. If replacing an existing target it checks emptiness and link-count sanity, rewrites the target entry to the old inode, and drops the replaced inode’s link count. If moving into a new name it adds a new link and adjusts the new parent count for directories. It then deletes the old entry and updates `..` when a directory crosses parents.

## Dependencies

Depends on directory-entry helpers declared in `minix.h`, MINIX inode allocation, page symlink helpers, VFS dentry aliasing and instantiation, folio kmap release helpers, and generic inode link-count helpers.

## Risks

Directory link-count consistency is the main risk. The code explicitly detects corrupted zero or too-low link counts in unlink/rmdir/rename. Rename has many partial states involving old entry, new entry, and directory `..`; failures must release folios and avoid leaking link-count changes.
