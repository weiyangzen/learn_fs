# File Research: sources/os/linux/linux-stable/fs/ext2/xattr.c

## Purpose

Implements ext2 extended attribute storage, lookup, listing, mutation, sharing, caching, and cleanup.

## On-Disk Model

Ext2 xattrs live in external filesystem blocks referenced by `EXT2_I(inode)->i_file_acl`. Each xattr block contains:

- `struct ext2_xattr_header`.
- Sorted variable-length xattr entries growing downward.
- A null terminator.
- Attribute values packed from the end of the block upward.

Identical xattr blocks can be shared by multiple inodes. Sharing is controlled by the xattr block header refcount and an `mb_cache` keyed by block content hash.

## Main Responsibilities

- Maps xattr namespace indexes to Linux xattr handlers.
- Gets xattr values with `ext2_xattr_get()`.
- Lists xattr names with `ext2_listxattr()` via `ext2_xattr_list()`.
- Creates, replaces, or removes xattrs with `ext2_xattr_set()`.
- Updates the superblock compat feature when xattrs are first introduced.
- Handles xattr block copy-on-write and sharing with `ext2_xattr_set2()`.
- Releases xattr blocks on inode deletion with `ext2_xattr_delete_inode()`.
- Maintains xattr block cache entries and hashes.

## Key Validation

- `ext2_xattr_header_valid()` requires `EXT2_XATTR_MAGIC` and exactly one disk block.
- `ext2_xattr_entry_valid()` rejects entries that run beyond the block, reference external value blocks, or point values beyond the permitted region.
- `ext2_xattr_cmp_entry()` relies on sorted namespace/name order.
- Bad xattr blocks call `ext2_error()` and return `-EIO`.

## Mutation Flow

`ext2_xattr_set()`:

- Validates name and value length.
- Initializes quotas.
- Takes `xattr_sem` for write.
- Reads existing xattr block if present.
- Locates the target sorted entry or insertion point.
- Computes free space.
- Enforces `XATTR_CREATE` and `XATTR_REPLACE`.
- Modifies in place only when the block refcount is one and no cache user is trying to reuse it.
- Otherwise clones the block into memory.
- Inserts/removes entry names and repacks values.
- Rehashes entries and delegates filesystem updates to `ext2_xattr_set2()`.

`ext2_xattr_set2()`:

- Searches for an identical cached xattr block.
- Reuses a found block by incrementing refcount and quota accounting.
- Keeps the old block if it was safely modified in place.
- Allocates a new block if no reusable block exists.
- Updates `i_file_acl`, inode ctime, inode metadata, and releases no-longer-used old blocks.

## Cache and Sharing

- `ext2_xattr_cache_insert()` inserts hash/block mappings into `mb_cache`, ignoring duplicate `-EBUSY`.
- `ext2_xattr_cache_find()` scans matching hash entries, reads candidate blocks, locks them, checks refcount ceiling, compares full block contents, and returns a locked matching buffer.
- `ext2_xattr_release_block()` either frees a singly referenced block or decrements refcount on a shared block, carefully serializing against concurrent reuse through `mb_cache_entry_delete_or_get()`.

## Dependencies

- Includes buffer heads, mbcache, quotaops, rwsems, security, `ext2.h`, `xattr.h`, and `acl.h`.
- Depends on ext2 allocation/freeing helpers, quota helpers, inode dirtying, and superblock feature update logic.

## Research Notes

This file is a compact copy-on-write metadata subsystem. The most important correctness concerns are block validation, sorted entries, packed value offsets, shared-block refcounts, and cache synchronization. The code avoids holding multiple buffer locks simultaneously to reduce deadlock risk.
