# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-checker.c

## Summary
Validates Btrfs tree blocks, leaf items, chunks, ownership, and parent key/level expectations when metadata is read or checked, rejecting corrupted structures with detailed diagnostics.

## Main Responsibilities
- Emit corruption diagnostics for generic items, file extents, directory items, block groups, chunks, devices, and extents.
- Validate item-specific content for common Btrfs key types.
- Validate whole-leaf key ordering, item offsets, item sizes, item packing, and required non-empty trees.
- Validate whole-node level, item count, child block pointers, and key ordering.
- Validate chunk items and superblock system chunks.
- Validate extent-buffer owner compatibility and expected first-key/level parent checks.

## Key APIs
- Leaf/node checks: `__btrfs_check_leaf()`, `btrfs_check_leaf()`, `__btrfs_check_node()`, `btrfs_check_node()`.
- Chunk check: `btrfs_check_chunk_valid()`.
- Parent/owner checks: `btrfs_check_eb_owner()`, `btrfs_verify_level_key()`.
- Dispatcher: `check_leaf_item()`.
- Major validators: `check_extent_data_item()`, `check_csum_item()`, `check_dir_item()`, `check_block_group_item()`, `check_leaf_chunk_item()`, `check_dev_item()`, `check_inode_item()`, `check_root_item()`, `check_extent_item()`, `check_extent_data_ref()`, `check_inode_ref()`, `check_inode_extref()`, `check_raid_stripe_extent()`, `check_remap_key()`, `check_dev_extent_item()`, free-space item validators.

## Important Behavior
File extent checks validate offset alignment, previous inode key consistency for fs trees, minimal item size, extent type, compression/encryption fields, inline extent rules, fixed size for regular/prealloc extents, sector alignment of disk/ram/offset/length fields, extent-end overflow, and overlap with the previous file extent in the same leaf.

Directory and inode-reference checks validate previous inode grouping, location-key type/range, file type, xattr consistency, name/data length bounds, item boundary containment, and hash match for dir/xattr items.

Block-group checks validate nonzero length, v1/v2 item size depending on remap-tree feature, chunk objectid/global-root id, used bytes, profile/type flags, remap feature gating, remap byte bounds, and identity remap count.

Chunk validation checks logical/length/sectorsize alignment, stripe length, chunk length upper bound, known type/profile flags, exactly one profile bit, required data/metadata/system type, mixed-group rules, remap feature gating, stripe count/sub-stripe rules, copy/parity constraints, and works both for leaf chunks and superblock sys-chunk array chunks.

Extent item checks validate skinny metadata feature gating, bytenr alignment, tree level, item size, generation, data/tree-block flag exclusivity, tree/data length rules, inline ref boundaries, ref type ordering, per-type sequence ordering, data-ref root/objectid/offset/count, shared-ref alignment/count, no padding, inline ref count not exceeding total refs, and overlap with previous extent items.

Whole-leaf validation requires level 0, written flag, valid non-empty roots for specific tree owners, globally increasing keys, tightly packed item data from the end of the leaf, item data within leaf bounds, no item/data overlap, and per-key item validation. Whole-node validation requires written flag, level in `[1, BTRFS_MAX_LEVEL)`, valid pointer count, nonzero aligned child block pointers, and increasing child keys.

`btrfs_check_eb_owner()` skips dummy tests, unknown owner `0`, log trees, and reloc trees. For non-subvolume trees, owner must match exactly; for subvolume trees, the extent buffer owner must also be a subvolume-tree id.

`btrfs_verify_level_key()` verifies expected level, optionally verifies first key for disk-read blocks whose generation is not newer than the last committed transaction, and rejects empty blocks when a first-key check is requested.

## Risks
Checker rules must be strict enough to reject fuzzed/corrupt images but not so strict that valid historical or feature-specific filesystems fail to mount. Feature-gated checks for remap tree, extent-tree v2, skinny metadata, simple quota, raid stripe tree, mixed groups, and read-only inode flags are especially sensitive.
