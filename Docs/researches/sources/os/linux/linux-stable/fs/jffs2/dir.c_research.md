# File Research: sources/os/linux/linux-stable/fs/jffs2/dir.c

## Role

Implements JFFS2 directory file operations and directory inode operations: lookup, readdir, create, link, unlink, symlink, mkdir, rmdir, mknod, and rename.

## VFS Operation Tables

- `jffs2_dir_operations` wires generic directory read, `jffs2_readdir`, ioctl, fsync, llseek, and file lease support.
- `jffs2_dir_inode_operations` wires create/lookup/link/unlink/symlink/mkdir/rmdir/mknod/rename plus ACL, setattr, and xattr listing hooks.

## Directory Lookup and Read

- `jffs2_lookup()` searches the inode-private sorted `dents` list by full-name hash, name length, name bytes, and highest version.
- `jffs2_readdir()` emits dot entries, then iterates the `dents` list, skipping deletion dirents with `ino == 0`.

## Creation Operations

- `jffs2_create()` allocates a raw inode, creates a JFFS2 inode, installs regular-file ops, and calls `jffs2_do_create()`.
- `jffs2_symlink()` writes a symlink raw inode containing the target path, caches the target in `f->target`, initializes security/ACLs, then writes a parent dirent.
- `jffs2_mkdir()` writes a metadata-only directory inode, sets initial link count, initializes security/ACLs, then writes a directory dirent and increments parent link count.
- `jffs2_mknod()` encodes device numbers for block/char special files, writes metadata inode data, initializes security/ACLs, then writes the dirent.

## Link and Removal Operations

- `jffs2_link()` rejects directory hard links, writes a new dirent via `jffs2_do_link()`, increments inode link accounting, and instantiates the dentry.
- `jffs2_unlink()` appends a deletion dirent through `jffs2_do_unlink()` and updates parent timestamps.
- `jffs2_rmdir()` first verifies no live child dirents remain, then unlinks and updates directory link counts.

## Rename

- Supports only default rename and `RENAME_NOREPLACE`; other flags return `-EINVAL`.
- Checks target directory emptiness when replacing a directory.
- Implements rename as link-new-name followed by unlink-old-name.
- Handles victim link count/inocache adjustments and parent link counts for moved directories.
- If unlink of the old name fails after link succeeds, it reports the failure, invalidates the new dentry, and leaves a hard-link-like result.

## Research Notes

The file reflects JFFS2’s log-structured design: namespace changes append new dirent nodes instead of rewriting directories in place. Several operations are two-stage inode-node plus dirent-node sequences, so error paths must treat partially created objects as normal deletion cases.
