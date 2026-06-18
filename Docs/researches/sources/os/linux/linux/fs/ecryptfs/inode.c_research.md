# File Research: sources/os/linux/linux/fs/ecryptfs/inode.c

## Purpose
Implements eCryptfs inode and namespace operations: inode interposition, lookup, create, link, unlink, symlink, mkdir, rmdir, mknod, rename, readlink, truncate/setattr, getattr, permission checks, xattr forwarding, ACL forwarding, and fileattr forwarding.

## Main Responsibilities
- Create upper inodes that wrap lower inodes and select the correct eCryptfs operation tables.
- Encode plaintext names before lower lookup/create and decode symlink targets on read.
- Initialize new regular files with eCryptfs metadata.
- Mirror lower inode attributes into upper inodes.
- Translate upper file sizes to lower file sizes for encrypted truncation.
- Forward metadata operations to lower VFS with `nop_mnt_idmap`.

## Inode Interposition
`__ecryptfs_get_inode()` rejects lower inodes from another lower superblock and rejects casefolded directories. It grabs the lower inode and uses `iget5_locked()` with lower-inode identity. `ecryptfs_inode_set()` stores the lower inode, copies attributes and size, sets inode number, assigns `ecryptfs_aops`, and selects inode/file operations based on mode.

## Lookup and Name Handling
`ecryptfs_lookup()` encrypts and encodes the requested dentry name when mount-wide filename encryption is enabled, looks up the lower dentry without permission recheck, then calls `ecryptfs_lookup_interpose()`. Interpose stores the lower dentry in upper `d_fsdata`, creates or reuses an upper inode, and for regular files reads metadata enough to initialize upper size.

Symlink creation encrypts and encodes the symlink target before calling lower `vfs_symlink()`. Reading a symlink uses lower `vfs_get_link()`, then decodes and decrypts the target.

## Creation and Removal
`ecryptfs_create()` calls `ecryptfs_do_create()` to create the lower inode and get the upper inode, then `ecryptfs_initialize_file()` writes eCryptfs headers. If initialization fails, it unlinks the lower file and marks the upper inode failed.

`link`, `mkdir`, `mknod`, `unlink`, `rmdir`, and `rename` are lower VFS operations wrapped by helper calls that lock or prepare lower dentries. After success they copy times, sizes, link counts, or full attributes upward as appropriate.

## Truncate and Setattr
`upper_size_to_lower_size()` maps visible upper size to lower size by adding metadata/header bytes and rounded data extents. `__ecryptfs_truncate()` handles expansion by writing one zero byte at the new end, handles plaintext passthrough truncation directly, and handles encrypted shrinking by zeroing the tail of the final upper page, updating metadata size via `ecryptfs_write_inode_size_to_metadata()`, then shrinking the lower file when needed.

`ecryptfs_setattr()` ensures crypt metadata is available before regular-file attribute changes if needed. It delegates size changes to `__ecryptfs_truncate()` and other changes to lower `notify_change()`.

## Metadata Forwarding
- Permission checks call `inode_permission()` on the lower inode.
- `getattr` fetches lower stat, mirrors attributes, fills upper stat, and preserves lower block count.
- Symlink getattr recomputes plaintext target size when filename encryption is active.
- xattr get/set/list/remove forward to lower inode operations under lower inode lock.
- ACL and fileattr operations forward to lower helpers and copy attributes after successful set.

## Operation Tables
- `ecryptfs_symlink_iops`: link target, permission, setattr, symlink getattr, listxattr.
- `ecryptfs_dir_iops`: full directory namespace operations plus fileattr and ACL.
- `ecryptfs_main_iops`: permission, setattr/getattr, listxattr, fileattr, ACL.
- `ecryptfs_xattr_handlers`: catch-all xattr handler forwarding to lower xattrs.

## Risks and Notes
- Casefolded lower directories are explicitly unsupported.
- Rename rejects all nonzero flags, so newer rename semantics are not implemented here.
- The code carefully handles negative lower dentries becoming positive during lookup, but races are still delegated to VFS primitives.
- Truncation mixes upper and lower size concepts and depends on crypto metadata being initialized before size decisions.
