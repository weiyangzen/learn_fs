# File Research: sources/os/linux/linux-stable/fs/jfs/namei.c

## Purpose

Implements JFS directory inode operations: create, mkdir, rmdir, unlink, link, symlink, rename, mknod, lookup, NFS export helpers, and case-insensitive dentry operations for OS/2-style mounts.

## Main Operation Patterns

- Creation paths (`jfs_create`, `jfs_mkdir`, `jfs_mknod`, `jfs_symlink`) initialize quota, convert dentries to JFS Unicode names, allocate the inode before directory search to avoid blocking while holding pinned dtree pages, start a transaction, lock parent/child commit mutexes, initialize ACL/security state, insert a dtree entry, set inode ops, mark dirty inodes, and commit.
- `jfs_rmdir()` validates directory emptiness with `dtEmpty()`, deletes the parent dtree entry, adjusts parent link count, clears EA/ACL extents through `txEA()`, clears target nlink, and commits deletion.
- `jfs_unlink()` deletes a directory entry and decrements the target link count. If the link count reaches zero, `commitZeroLink()` frees persistent resources and may require repeated `xtTruncate_pmap()` transactions after commit.
- `jfs_link()` inserts another dtree reference and increments the target nlink, rejecting read-only inodes.
- `jfs_symlink()` stores small symlink targets inline as fast symlinks, while larger targets are stored in one xtree-backed extent written through metapages.
- `jfs_rename()` supports only `RENAME_NOREPLACE` among flags. It verifies both source and destination dtree state before transaction work, handles replacement victim deletion/truncation, updates directory parent `..` metadata when moving directories, and commits all changed inodes.
- `jfs_lookup()` searches the directory dtree and returns `d_splice_alias()` around `jfs_iget()`.

## Zero-Link Resource Handling

`commitZeroLink()` handles regular files and non-fast symlinks by marking the transaction `COMMIT_PMAP`, logging EA/ACL extent frees, and calling `xtTruncate_pmap()`. `jfs_free_zero_link()` later frees EA/ACL/data resources from the working map and cache once the unlinked open file is finally released.

## VFS Exports

`jfs_dir_inode_operations` wires standard directory methods plus xattrs, setattr, fileattr, and POSIX ACL hooks. `jfs_dir_operations` wires read, iterate, fsync, ioctl, llseek, and leases. Export helpers use generic file-handle decode with inode generation validation and directory parent lookup via `i_dtroot.header.idotdot`.

## Case-Insensitive Dentries

`jfs_ci_hash()` and `jfs_ci_compare()` fold ASCII bytes with `tolower()`. `jfs_ci_revalidate()` keeps positive dentries valid but drops negative dentries for create/rename-target intents so the user-supplied case is used.

## Locking And Error Notes

The code relies on VFS inode locking plus JFS `commit_mutex` nesting classes. Paths that modify file data on zero-link deletion also take `IWRITE_LOCK`. Directory index truncation may be incomplete and is retried when `COMMIT_Stale` is observed. Several paths abort transactions differently for `-EIO` versus expected allocation/full errors, with `-EIO` marking the filesystem dirty.
