# File Research: sources/os/linux/linux-stable/fs/ext4/xattr.c

## Purpose
Implements ext4 extended attribute storage, lookup, listing, mutation, sharing, validation, and teardown. It supports in-inode xattrs, one external xattr block per inode, shared identical xattr blocks via mbcache, and large xattr values stored in special EA inodes.

## Main Components
- Xattr handler maps connect ext4 namespace indexes to VFS xattr handlers for `user`, `trusted`, POSIX ACL, `security`, and `hurd`.
- `check_xattrs()` validates both external xattr blocks and in-inode xattr regions: magic, block count, metadata checksum, entry bounds, name length, value bounds, EA-inode references, and maximum value size.
- `ext4_xattr_get()` first checks the inode body, then the external block, under `EXT4_I(inode)->xattr_sem`.
- `ext4_listxattr()` lists in-inode names first and then block names, filtering by namespace visibility through xattr handler permissions.
- Mutation flows through `ext4_xattr_set_handle()`, which reserves inode write access, enforces `XATTR_CREATE`/`XATTR_REPLACE`, tries ibody storage first, falls back to xattr block storage, and may use EA inode storage for large values.
- External block mutation in `ext4_xattr_block_set()` handles in-place updates for exclusive blocks, clone-on-write for shared blocks, reuse of identical cached blocks, allocation of new metadata blocks, checksum updates, and release of replaced blocks.
- `ext4_xattr_set_entry()` performs the low-level packed-entry/value layout edits, including value compaction, entry insertion/removal, hash recalculation, and EA-inode reference release.
- Large EA inode support includes hash/refcount encoding, cache lookup, creation, quota charging, read/write, refcount increment/decrement, orphan transitions, and Lustre legacy compatibility.
- Inode extra-isize expansion can move selected xattrs from ibody to external blocks and shift xattr entries to make room.
- Delete/evict paths release xattr blocks, decrement EA-inode references, free quota, clear `i_file_acl`, and defer `iput()` through `ext4_xattr_inode_array`.

## Important Behaviors
- External xattr block checksums use filesystem checksum seed plus disk block number and header contents with the checksum field zeroed.
- Shared xattr blocks are protected by buffer locks and mbcache reusable flags; blocks at `EXT4_XATTR_REFCOUNT_MAX` are not reusable.
- EA inode values are protected by CRC/hash verification; the code also accepts and warns about an older signed-char name hash variant.
- Journal credit estimation accounts for owner inode updates, old/new xattr blocks, quota updates, inline-data expansion, EA inode creation/deletion, data blocks, and reference updates.
- Fast commit is marked ineligible for xattr mutations.
- Quota accounting charges the parent inode for shared EA inode storage, while EA inodes themselves are marked `S_NOQUOTA`.

## Dependencies
Uses ext4 journaling, quota, mbcache, inode allocation, block mapping, orphan handling, fast commit state, inline-data helpers, POSIX ACL handler stubs, and metadata checksum helpers.

## Research Notes
This is a high-risk metadata file. Key invariants are packed xattr layout bounds, xattr block refcounts, EA-inode refcounts, quota symmetry, checksum/hash correctness, and transaction credit sufficiency.
