# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext_attr.c

## Purpose
Implements ext2/ext4 extended attribute block IO, hashing, refcounting, xattr handle operations, POSIX ACL conversion, inline-inode EA storage, EA block storage, and external EA inode storage.

## Major Behavior
- Computes EA entry hashes with unsigned and legacy signed name handling.
- Supports `ea_inode` values by folding the referenced EA inode hash into the entry hash.
- Rehashes whole EA blocks from per-entry hashes.
- Stores EA inode hash/refcount in selected inode timestamp/version fields.
- Reads/writes EA blocks with checksum verification/update and big-endian swapping.
- Adjusts shared EA block refcounts.
- Frees EA blocks from inodes and decrements block/inode accounting.
- Prepares EA blocks for writes, including copy-on-write when a block is shared.
- Converts between POSIX ACL xattr format and ext4 compact on-disk ACL format.
- Serializes xattrs into inode body and/or external EA block.
- Parses xattrs from inode body and EA block with bounds checks for name length, value size, value offset, and external EA inode validity.
- Validates xattr hashes, including older signed-hash compatibility and old Lustre-style EA inode references.
- Opens/closes xattr handles and maintains an in-memory array split by `ibody_count` into inode-body attrs and EA-block attrs.
- Gets, sets, iterates, removes, removes all, counts, and flags xattrs.
- Creates external EA inodes for large values when the feature is available.
- Decrements and frees external EA inodes when references are removed.

## Important Data Structures
- `struct ext2_xattr`: in-memory xattr record with full name, short name, name index, value buffer, length, and optional EA inode.
- `struct ext2_xattr_handle`: active xattr context with fs, inode number, array capacity/count, inode-body count, and flags.
- `ea_names`: prefix table mapping full xattr names to disk name indexes.

## Mutation Flow
`ext2fs_xattr_set`:
1. Converts POSIX ACLs unless raw mode is active.
2. Detects no-op updates for identical inline values.
3. Reads inode and computes free inode-body space.
4. Reserves `system.data` for inode body only.
5. Computes EA block free space.
6. Chooses external EA inode storage for large values when enabled.
7. Updates the sorted in-memory array and writes back inode/EA block.

`ext2fs_xattrs_write`:
1. Reads inode.
2. Initializes `i_extra_isize` if needed.
3. Writes inode-body xattrs if space exists.
4. Writes remaining attrs to an EA block, allocating/COWing as necessary.
5. Frees a stale EA block if attrs shrink into inode body only.
6. Writes inode back.

## Dependencies
Relies on:
- `ext2fs_read_inode_full`, `ext2fs_write_inode_full`, `ext2fs_write_new_inode`.
- `ext2fs_file_open/read/write/close`.
- `ext2fs_file_acl_block(_set)`.
- `ext2fs_ext_attr_block_csum_verify/set`.
- `ext2fs_alloc_block2`, block allocation stats, inode allocation stats.
- `ext2fs_iblk_add_blocks/sub_blocks`.
- `ext2fs_punch` for freeing EA inode data.
- xattr format macros from `ext2_ext_attr.h`.

## Risks and Notes
- Boundary validation in `read_xattrs_from_buffer` is critical; malformed xattrs can otherwise point values into entry space or beyond the storage region.
- Shared EA blocks require copy-on-write before mutation.
- External EA inode lifetime must keep refcounts, link count, allocation stats, and data blocks consistent.
- `system.data` inline data has special placement rules.
- Hash compatibility accepts both unsigned and signed historical forms.
