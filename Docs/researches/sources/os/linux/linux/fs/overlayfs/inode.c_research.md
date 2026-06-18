# File Research: sources/os/linux/linux/fs/overlayfs/inode.c

## Role

Implements OverlayFS inode operations, stat/inode number mapping, permission checks, ACL handling, file attributes, inode allocation/lookup, nlink metadata, and operation tables.

## Main Responsibilities

- `ovl_setattr()` prepares VFS attribute changes, chooses metadata-only or full-data copy-up for truncation, clears `ATTR_FILE`/`ATTR_OPEN`, applies changes to upper, and copies attributes back.
- `ovl_getattr()` gathers real stats, maps device/inode numbers through samefs/xino/fsid rules, handles metacopy block counts, forces merged directory nlink to 1, and reports overlay nlink for indexed inodes.
- `ovl_permission()` checks overlay inode permissions with caller credentials and real inode permissions with mounter credentials; write access to lower regular files is converted to read permission for future copy-up.
- Symlink, fiemap, update-time, ACL, and fileattr operations delegate to real paths with overlay credential handling.
- POSIX ACL code clones and remaps ACL entries for idmapped lower/upper mounts.
- Fileattr operations use a temporary file open for LSM ioctl checks, preserve immutable/append-only via OverlayFS protection xattrs, and merge protection flags into reported attributes.
- Defines inode operation tables for files, symlinks, special files, and address-space operations.
- Annotates inode locks for nested OverlayFS lockdep stack depths.
- Maps inode numbers using samefs, xino high bits, or non-persistent overlay inode numbers.
- Maintains indexed nlink xattr format with `U+/-N` or `L+/-N`.
- Provides inode cache lookup, trap inode creation for layer-root loop detection, hashing by lower/upper inode, and `ovl_get_inode()` construction.

## Important Control Flow

`ovl_get_inode()` decides whether an overlay inode should be keyed by lower inode, upper inode, or allocated un-hashed based on lower presence, index state, upper presence, hardlink risk, and NFS export configuration. Existing cached inodes are verified against supplied upper/lower dentries before reuse.

`ovl_hash_bylower()` is central to identity: pure uppers are not hashed by lower, indexed objects are, read-only lower objects are, but lower hardlinks that may break on copy-up and non-indexed NFS-export uppers avoid lower hashing.

## Edge Cases

- Trap inodes intentionally fail verification to prevent layer-root recursion/loops.
- Directory inode numbers may be non-persistent when xino cannot uniquely map all layers.
- `update_time()` only updates upper atime and returns `-EAGAIN` for NOWAIT atime updates.
- ACL removal from lower first checks whether the ACL exists before copy-up.

## Dependencies

Uses OverlayFS layer/path helpers, xattrs, index flags, lockdep, POSIX ACL APIs, fileattr APIs, VFS stat and permission helpers, and inode cache primitives.

## Research Notes

This file is the inode identity and metadata authority for OverlayFS. It reconciles VFS-visible inode state with real upper/lower inode state while preserving copy-up, export, hardlink, and idmapped mount semantics.
