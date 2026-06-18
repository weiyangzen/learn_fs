# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-checker.c

## Role

Btrfs metadata validation layer for tree blocks. It validates leaves, nodes, chunks, item layouts, item contents, owner/parent expectations, and key-level relationships when tree blocks are read or otherwise checked.

## Diagnostics

- `generic_err()`, `file_extent_err()`, `dir_item_err()`, `block_group_err()`, `chunk_err()`, `dev_item_err()`, and `extent_err()` produce structured corruption messages and page dumps.
- Errors generally return `-EUCLEAN` through wrappers or `BTRFS_TREE_BLOCK_*` status codes internally.

## Leaf Item Validators

- File extents: `check_extent_data_item()` validates offset alignment, previous inode key continuity, item size/type, compression/encryption fields, inline extent rules, regular/prealloc alignment, overflow, and overlap with previous file extent.
- Checksums: `check_csum_item()` validates objectid, offset alignment, item size alignment, and overlap with previous csum range.
- Directory/xattr items: `check_dir_item()` validates previous inode continuity, embedded location keys, file type, xattr/data length constraints, boundary safety, and name-hash match.
- Inode refs/extrefs: `check_inode_ref()` and `check_inode_extref()` validate packed variable-length name records do not overflow item bounds.
- Inode items: `check_inode_item()` validates key, item size, generation/transid bounds, mode bits/type, directory nlink, and inode flags/ro-compat flags.
- Root items: `check_root_item()` validates key, legacy/current item size, generation fields, bytenr alignment, level/drop level, interrupted-drop checkpoint sanity, and root flags.
- Block groups: `check_block_group_item()` validates item size by feature, chunk objectid/global root id, used bytes, profile/type flags, remap/remapped feature gating, remap bytes, and identity remap count.
- Chunks: `check_leaf_chunk_item()` validates chunk item size then delegates to `btrfs_check_chunk_valid()`.
- Devices: `check_dev_item()` validates dev item objectid, size, devid match, and bytes used <= total.
- Device extents: `check_dev_extent_item()` validates chunk tree/objectid, alignment, length, and overlap with previous extent.
- Extent items/backrefs: `check_extent_item()`, `check_simple_keyed_refs()`, and `check_extent_data_ref()` validate extent alignment, skinny metadata gating, tree/data flag consistency, generation, tree block info, inline ref bounds/order/counts, keyed ref sizes, data-ref root/objectid/offset/count, and extent overlap.
- RAID stripe extents: `check_raid_stripe_extent()` validates alignment and `RAID_STRIPE_TREE` incompat feature.
- Remap keys: `check_remap_key()` validates `REMAP_TREE` feature, item size by key type, nonzero aligned length, aligned objectid, and overflow.
- Free-space tree items: `check_free_space_info()`, `check_free_space_extent()`, and `check_free_space_bitmap()` validate alignment, item size, flags, extent count, zero-sized extent item, and bitmap byte count.

## Chunk Validation

`btrfs_check_chunk_valid()` is shared by leaf chunk items and superblock sys chunk array checks. It validates:

- nonzero stripes except remapped chunks;
- stripe count versus copies/parity/profile;
- logical/length/sector-size alignment;
- stripe length equal to `BTRFS_STRIPE_LEN`;
- overflow and artificial maximum chunk size;
- recognized block group flags;
- exactly one profile bit where applicable;
- type flag presence and system/data/metadata exclusivity;
- mixed-group gating;
- remap feature gating;
- profile-specific stripe/sub-stripe counts.

## Leaf and Node Checks

- `__btrfs_check_leaf()`: validates level zero, `WRITTEN` flag, empty-leaf rules by owner/tree/features, strict key ordering, packed item offsets with no holes/overlap, item data inside leaf bounds, item pointer not overlapping item array, then dispatches to item-specific validators.
- `btrfs_check_leaf()`: converts non-clean status to `-EUCLEAN` and allows error injection.
- `__btrfs_check_node()`: validates `WRITTEN`, level range, item count, child block pointer nonzero/aligned, and node key ordering.
- `btrfs_check_node()`: wrapper returning `-EUCLEAN` and allowing error injection.

## Parent/Owner Checks

- `btrfs_check_eb_owner()`: verifies extent-buffer owner against expected root, with exceptions for testing, unknown owner checks, log trees, relocation trees, and subvolume-owner equivalence.
- `btrfs_verify_level_key()`: verifies expected level and optional first key from parent context, skipping first-key checks for live blocks newer than the last committed transaction.

## Important Constraints

- Validators intentionally rely only on item-local data and immediate previous key/item where possible.
- Some checks are feature-gated to avoid rejecting valid older or feature-specific filesystems.
- Empty extent trees are allowed with `EXTENT_TREE_V2`; several other core trees must not be empty.
