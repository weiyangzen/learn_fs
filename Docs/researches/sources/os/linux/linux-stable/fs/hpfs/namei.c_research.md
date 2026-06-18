# File Research: sources/os/linux/linux-stable/fs/hpfs/namei.c

## Purpose

Implements HPFS namespace mutation operations: create, mkdir, mknod, symlink, unlink, rmdir, rename, and symlink page reads.

## Main Entry Points

- `hpfs_create()`
- `hpfs_mkdir()`
- `hpfs_mknod()`
- `hpfs_symlink()`
- `hpfs_unlink()`
- `hpfs_rmdir()`
- `hpfs_rename()`
- `hpfs_symlink_read_folio()`
- `hpfs_dir_iops`, `hpfs_symlink_aops`

## Control Flow And State

Create and mkdir validate names, allocate fnodes and optionally dnodes, construct directory entries, instantiate inodes, insert dirents into the parent dnode tree, fill fnodes, update current uid/gid/mode through EAs if needed, and update parent directory times. Special files and symlinks require EA write support because their mode/device/target are stored in EAs; symlink contents use a `SYMLINK` EA read through a folio operation.

Unlink and rmdir locate the dirent, reject protected sentinel entries and wrong file types, remove the dirent through `hpfs_remove_dirent()`, and drop link counts. Rmdir first counts items in the target directory tree.

Rename supports only `RENAME_NOREPLACE`. It rejects overwriting directories, copies the old dirent, removes or replaces target entries, inserts into the new directory, removes the old entry, updates parent link counts for directories, and rewrites the fnode parent/name fields.

## Dependencies

Uses allocation, dnode mutation, EA writing, inode initialization/writeback, time conversion, and global HPFS locking.

## Risks

Namespace updates involve multi-step metadata mutation without journaling. Several failure paths can return ENOSPC/EFSERROR after partial work, relying on conservative preflight and cleanup. Rename-over-file updates the existing target dirent after removing the old one, so consistency depends on successful target lookup after deletion.
