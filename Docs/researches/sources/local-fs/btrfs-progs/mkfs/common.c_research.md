# File Research: sources/local-fs/btrfs-progs/mkfs/common.c

## Purpose
Common mkfs implementation for creating the initial btrfs filesystem image and validating target devices/files before formatting.

## Key Creation Flow
- `make_btrfs(fd, cfg)` assembles a temporary-signature filesystem with initial system chunk, root tree, extent tree, chunk tree, device tree, fs tree, checksum tree, optional free-space tree, and optional block-group tree.
- Initializes UUIDs, superblock fields, feature flags, csum type, label, device item, sys chunk array, and initial tree blocks.
- Writes all initial tree blocks with checksums, then writes the superblock using `BTRFS_MAGIC_TEMPORARY` and `sbwrite()`, followed by `fsync()`.

## Important Helpers
- `btrfs_write_empty_tree()` writes an empty leaf/tree root for a given objectid.
- `btrfs_create_tree_root()` creates root items for initial trees and initializes the FS tree root UUID/timestamps.
- `create_free_space_tree()` writes free-space info and one free extent for the initial system group.
- `write_block_group_item()` and `create_block_group_tree()` serialize block group items, including v2/remap-tree fields.
- `zoned_system_group_offset()` chooses a system group zone that avoids superblock zones.
- `mkfs_blocks_add()` and `mkfs_blocks_remove()` maintain the initial tree-block list.
- `btrfs_min_dev_size()` estimates minimum device size for zoned, mixed, single, and profiled data/metadata layouts.
- `test_dev_for_mkfs()`, `test_status_for_mkfs()`, `test_minimum_size()`, `is_swap_device()`, and `check_overwrite()` protect against formatting swap, mounted, too-small, or already-formatted devices.

## Dependencies
Uses btrfs shared accessors/disk-io/volume/zoned code, common feature definitions, open/device/string/message helpers, libblkid probing, and UUID generation.

## Notable Behaviors
- Initial filesystem uses one system chunk mapped 1:1 at the reserved/system offset.
- Free-space-tree and block-group-tree initialization is feature-flag controlled.
- Zoned mode uses zone-sized system groups and sets cache generation differently.
- Existing signatures are detected with blkid and a manual zoned btrfs signature fallback at offset 0.
- `/proc/swaps` entries are decoded for octal escapes before stat comparisons.

## Risks And Review Notes
- `mkfs_blocks_add()` uses `memmove(blocks + i + 1, blocks + i, *blocks_nr - i)` with a byte count that is missing `sizeof(*blocks)`. Because enum size is usually 4 bytes, this moves too few bytes when inserting before existing entries. Current call patterns may avoid harmful insertion positions, but the helper itself is wrong.
- `check_overwrite()` treats blkid probe errors and “nothing found” as reasons to run the zoned-signature fallback; this is conservative, but can produce warnings from devices that are unreadable at offset 0.
- `force_overwrite` skips signature checks but not mount checks unless mount status cannot be determined, where it warns and proceeds.
- `make_btrfs()` writes a temporary magic superblock; callers must finalize the filesystem after this initial image phase.
