# File Research: sources/local-fs/btrfs-progs/check/mode-common.c

## Scope

This file implements repair and validation utilities shared by original and low-memory Btrfs check modes: checksum range counting/reconstruction, inode-item creation and mode repair, lost+found linking, tree-child validation, metadata exclusion, device/super repairs, and subvolume orphan repair.

## Public APIs Covered

- `check_prealloc_extent_written()` detects whether a preallocated extent has been written through another reference.
- `count_csum_range()` counts csum-covered bytes in a logical range.
- `insert_inode_item()` creates an inode item with current timestamps and conservative metadata.
- `link_inode_to_lostfound()` creates `lost+found` and links otherwise unreferenced inodes into it.
- `check_dev_size_alignment()`, `check_child_node()`, `reada_walk_down()`.
- Metadata allocation safety helpers: `reset_cached_block_groups()`, `pin_metadata_blocks()`, `exclude_metadata_blocks()`, `cleanup_excluded_extents()`.
- Directory and inode-mode repair helpers: `delete_corrupted_dir_item()`, `detect_imode()`, `reset_imode()`, `repair_imode_common()`, `check_repair_free_space_inode()`.
- Repair helpers: `recow_extent_buffer()`, `get_extent_item_generation()`, `repair_dev_item_bytes_used()`, `fill_csum_tree()`, `check_and_repair_super_num_devs()`, `repair_subvol_orphan_item()`.

## Control Flow And Behavior

- Prealloc csum validation walks inline and keyed extent refs, then consults referenced file extents to distinguish truly odd prealloc csums from valid shared written extents.
- `count_csum_range()` searches the csum tree, steps across csum items, and accumulates only overlapping covered bytes.
- Lost+found repair chooses a new inode number, creates `lost+found`, links the inode, and appends `.INO` suffixes when names conflict.
- Child-node validation compares parent key, block pointer, and generation against the child header/first key.
- Inode mode detection uses root-inode special handling, inode refs plus matching dir items/indexes, directory/file extent hints, and rdev fallback.
- Checksum tree rebuild can traverse fs trees or extent trees. It reads data sectors, inserts csums, then removes csums for NODATASUM or preallocated ranges.
- Super `num_devices` repair counts device items in the chunk tree and writes all superblocks without a transaction.
- Device item bytes-used repair updates in-memory device accounting before starting a transaction to avoid allocation side effects.

## State And Dependencies

- Defines global `g_task_ctx`.
- Uses global check state from `mode-common.h`: `gfs_info`, options such as `opt_check_repair`, and accounting globals.
- Depends on Btrfs transaction, tree search, extent/backref, csum, device, and repair APIs.

## Risks And Invariants

- Repair helpers frequently release and reacquire paths because COW can invalidate old paths.
- Csum reconstruction must avoid adding invalid checksums for NODATASUM and unwritten prealloc extents.
- `insert_inode_item()` is intentionally incomplete and warns users to inspect permissions/content.
- Metadata exclusion and pinning are repair-safety mechanisms; failing them risks overwriting metadata during fsck repair.
