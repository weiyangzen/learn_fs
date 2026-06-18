# File Research: sources/os/linux/linux-stable/fs/bad_inode.c

## Purpose
Provides VFS stub operations for inodes that could not be read or became invalid due to I/O or remote filesystem errors.

## Main Interfaces
- `make_bad_inode()`.
- `is_bad_inode()`.
- `iget_failed()`.

## Important Behavior
`bad_inode_ops` implements common inode operations by returning `-EIO`, including create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, rename, permission, getattr, setattr, xattr listing, get_link, ACL, fiemap, update_time, atomic_open, tmpfile, and set_acl. `bad_file_ops` rejects open with `-EIO`.

`make_bad_inode()` removes the inode from the inode hash, resets it as a regular file with simple timestamps, installs bad inode/file operations, and clears xattr operation flags. `iget_failed()` marks an under-construction inode bad, unlocks it, and drops it.

## Cross-File Relationships
Called by filesystem inode lookup/read paths that fail after allocating an inode. VFS users can test with `is_bad_inode()`.

## Risks / Review Notes
The goal is fail-closed behavior: after marking bad, operations should consistently return `-EIO` rather than proceeding with partially initialized filesystem state.
