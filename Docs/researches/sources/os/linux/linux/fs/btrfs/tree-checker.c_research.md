# File Research: sources/os/linux/linux/fs/btrfs/tree-checker.c

## Purpose

This file implements Btrfs tree block validation. It checks nodes and leaves read from disk for structural consistency and item-level sanity before normal filesystem code trusts their contents. It is intended to catch fuzzed/corrupt images and internal bugs while avoiding false rejection of valid historical filesystems.

## Diagnostic Helpers

- `generic_err()`: common corrupt leaf/node reporter with root, block, slot, and page dump.
- `file_extent_err()`: file extent reporter including inode and file offset.
- `dir_item_err()`: directory/xattr reporter including inode.
- `block_group_err()`: block group reporter including start and length.
- `chunk_err()`: chunk reporter for either chunk tree leaves or superblock syschunk array.
- `dev_item_err()`, `extent_err()`, and `inode_ref_err()`: specialized diagnostics.

Detected corruption generally returns `-EUCLEAN` through item validators or maps to `-EUCLEAN` in public wrappers.

## File Extent and Csum Validation

`check_extent_data_item()` validates:
- File offset alignment.
- Previous key objectid continuity for inode-related items in subvolume trees.
- Minimum item size and valid file extent type.
- Compression range and zero encryption.
- Inline extent offset and uncompressed inline size.
- Regular/prealloc fixed item size.
- Alignment of ram bytes, disk bytenr, disk bytes, offset, and num bytes.
- Extent-end overflow.
- Overlap with the previous file extent in the same leaf.
- Debug-only ram/disk size mismatch for uncompressed extents.

`file_extent_end()` computes the logical end used for overlap checking.

`check_csum_item()` validates:
- Objectid is `BTRFS_EXTENT_CSUM_OBJECTID`.
- Key offset is sectorsize aligned.
- Item size is checksum-size aligned.
- Adjacent csum item ranges do not overlap.

## Inode, Directory, and Xattr Validation

`check_prev_ino()` detects missing inode-item ordering context for inode-related keys in subvolume trees.

`check_inode_key()` validates inode location keys and requires xattr location keys to be zero.

`check_root_key()` validates root ids, relocation-root rules, and prevents directory-like references to non-fs trees.

`check_dir_item()` iterates packed `struct btrfs_dir_item` entries and validates:
- Header and payload bounds.
- Location key type and value.
- Directory file type.
- Xattr key/type consistency.
- Name/data length limits.
- Non-xattr data length is zero.
- DIR_ITEM/XATTR key hash matches the item name.

`check_inode_item()` validates:
- Item size.
- Inode generation and transid against super generation + 1.
- Mode bit mask and file type.
- Directory nlink <= 1.
- Inode incompat and ro-compat flags, rejecting unknown ro flags on writable mounts.

`check_inode_ref()` and `check_inode_extref()` validate packed inode ref/extref entry boundaries and nonzero name payload shape.

## Root Item Validation

`check_root_item()`:
- Validates key rules through `check_root_key()`.
- Accepts modern and legacy root item sizes.
- Checks generation, generation_v2, and last_snapshot against super generation + 1.
- Checks root bytenr alignment.
- Checks root and drop levels below `BTRFS_MAX_LEVEL`.
- Rejects nonzero `drop_progress.objectid` with `drop_level == 0`.
- Allows only readonly and dead root flags.

## Block Group and Chunk Validation

`check_block_group_item()` validates:
- Nonzero block group length.
- Item size based on whether remap tree is enabled.
- Chunk objectid/global root id rules.
- Used bytes <= block group length.
- At most one profile bit.
- Metadata remap/remapped flags require remap-tree incompat.
- Type is one of allowed data/metadata/system/remap/mixed values.
- V2 remap bytes and identity remap count within block group bounds.

`valid_stripe_count()` encodes profile-specific stripe/sub-stripe constraints.

`btrfs_check_chunk_valid()` validates chunk items and superblock syschunk entries:
- Stripe count, copies, and parity constraints unless remapped.
- Logical address alignment.
- Sector size match.
- Nonzero aligned length and no logical+length overflow.
- Stripe length equals `BTRFS_STRIPE_LEN`.
- Chunk length below the artificial maximum.
- Recognized type/profile flags.
- Exactly one or zero profile bits.
- Required type flag.
- System chunks do not mix with data/metadata.
- Mixed data/metadata chunks require mixed-groups feature.
- Remap flags require remap-tree feature.
- Profile-specific stripe/sub-stripe count validity.

`check_leaf_chunk_item()` adds leaf item size validation before calling the common chunk validator.

## Device and Dev Extent Validation

`check_dev_item()` validates:
- Key objectid is `BTRFS_DEV_ITEMS_OBJECTID`.
- Item size.
- Device id matches key offset.
- Bytes used does not exceed total bytes.

`check_dev_extent_item()` validates:
- Chunk tree id and chunk objectid.
- Key offset, chunk offset, and length alignment.
- No overlap with previous dev extent for the same device.

## Extent and Backref Validation

`check_extent_item()` validates `BTRFS_EXTENT_ITEM_KEY` and `BTRFS_METADATA_ITEM_KEY`:
- Skinny metadata feature requirement.
- Bytenr alignment.
- Metadata key level bounds.
- Minimum extent item size.
- Generation <= super generation + 1.
- Exactly one of DATA or TREE_BLOCK flags.
- Tree extent length/nodesize rules.
- Data extent key type, length alignment, and no full-backref flag.
- Tree block info level for non-skinny tree extents.
- Inline ref bounds, allowed ref types, alignment, objectid/root validity, and nonzero counts.
- Inline ref ordering by type and descending sequence/hash.
- No padding.
- Inline ref count not greater than total refs.
- Previous extent item does not overlap the current one.

`check_simple_keyed_refs()` validates simple keyed backrefs, including item size and alignment.

`check_extent_data_ref()` validates arrays of keyed data refs for item-size alignment, root/objectid/offset validity, and nonzero count.

`is_valid_dref_root()` permits data backrefs from subvolume trees, data reloc tree, and root tree.

## RAID Stripe, Remap, and Free-Space Validation

`check_raid_stripe_extent()`:
- Requires aligned objectid.
- Requires `RAID_STRIPE_TREE` incompat feature.

`check_remap_key()`:
- Requires `REMAP_TREE`.
- Validates item sizes for identity/remap/backref keys.
- Requires nonzero aligned length and aligned objectid.
- Rejects objectid+length overflow.

`check_free_space_info()`:
- Validates aligned block group range key.
- Validates item size and flags.
- Checks extent count does not exceed maximum sectors in the range.

`check_free_space_extent()`:
- Validates aligned key and zero item size.

`check_free_space_bitmap()`:
- Validates aligned key.
- Requires nonzero length.
- Requires exact bitmap item size for the represented range.

## Leaf Validation

`check_leaf_item()` dispatches by key type to item-specific validators.

`__btrfs_check_leaf()` performs whole-leaf checks:
- Header level must be 0.
- `BTRFS_HEADER_FLAG_WRITTEN` must be set.
- Certain roots must not have empty leaves, with exceptions for relocation and extent-tree-v2 empty extent trees.
- Keys must be strictly increasing.
- Item data must be contiguous from the end of the leaf, with no holes or overlaps.
- Item data must stay inside the leaf data area.
- Item data must not overlap item headers.
- Each item must pass item-specific validation.

`btrfs_check_leaf()` maps non-clean status to `-EUCLEAN` and supports error injection.

## Node Validation

`__btrfs_check_node()` validates:
- `BTRFS_HEADER_FLAG_WRITTEN`.
- Level in `[1, BTRFS_MAX_LEVEL - 1]`.
- Nritems in `[1, BTRFS_NODEPTRS_PER_BLOCK]`.
- Nonzero aligned block pointers.
- Strictly increasing node keys.

`btrfs_check_node()` maps non-clean status to `-EUCLEAN` and supports error injection.

## Ownership and Parent Checks

`btrfs_check_eb_owner()`:
- Skips dummy selftest fs, unknown owner `0`, log tree, and reloc tree cases.
- For non-subvolume trees, extent buffer owner must equal root owner.
- For subvolume trees, owner may differ but must still be a valid subvolume tree id.

`btrfs_verify_level_key()`:
- Verifies extent buffer level against expected parent check level.
- Optionally verifies first key.
- Skips first-key verification for live tree blocks newer than the last committed transaction.
- Rejects empty tree blocks when a first-key check is required.
- Compares expected first key to the first node/item key.

## Important Invariants

- Validators must not reject valid historical formats, so legacy root item sizes and selective strictness are supported.
- Item checks rely on item data and local key ordering, not broader tree traversal.
- Feature-gated formats such as skinny metadata, RAID stripe tree, remap tree, mixed groups, and extent-tree-v2 are explicitly checked.
- Empty-tree allowances depend on root type and feature flags.
- `-EUCLEAN` is the standard corruption result.

## Research Notes

`tree-checker.c` is a defensive boundary between raw on-disk metadata and normal Btrfs code. Its highest-risk maintenance area is balancing stricter corruption detection against compatibility with valid existing filesystems.
