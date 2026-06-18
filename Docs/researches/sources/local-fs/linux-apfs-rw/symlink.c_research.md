# File Research: sources/local-fs/linux-apfs-rw/symlink.c

## Purpose

`symlink.c` implements APFS symlink target resolution and defines inode operations for symlink inodes.

## Main Flow

`apfs_get_link()` takes the container read lock, rejects RCU/pathwalk calls without a dentry by returning `-ECHILD`, reads the symlink extended attribute size with `__apfs_xattr_get()`, allocates a target buffer, reads the target xattr, validates that it is non-empty and null-terminated, releases the APFS read lock, and returns the buffer with a delayed `kfree_link` cleanup.

The symlink target is stored in the `APFS_XATTR_NAME_SYMLINK` xattr rather than inline inode data.

## Inode Operations

`apfs_symlink_inode_operations` wires:

- `.get_link = apfs_get_link`
- `.getattr = apfs_getattr`
- `.listxattr = apfs_listxattr`
- `.update_time = apfs_update_time`
- `.readlink = generic_readlink` on kernels before 4.10

## Invariants And Risks

- Symlink targets must be null-terminated on disk.
- Empty targets are treated as corruption.
- The APFS container read lock protects xattr lookup and read.
- Allocation size comes from a first xattr size query, so races are constrained by the filesystem-wide lock.

## Test Focus

Test valid symlink reads, missing symlink xattr, empty or unterminated targets, allocation failure, RCU pathwalk fallback via `-ECHILD`, xattr listing, and timestamp updates on symlink inodes.
