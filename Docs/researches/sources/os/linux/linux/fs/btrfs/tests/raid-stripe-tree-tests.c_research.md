# File Research: sources/os/linux/linux/fs/btrfs/tests/raid-stripe-tree-tests.c

## Purpose

This file implements Btrfs selftests for RAID stripe tree operations. It builds dummy filesystems with a `stripe_root`, synthetic devices, and dummy transactions, then verifies create, lookup, update, and delete behavior for RAID stripe extents.

The tests focus on edge cases in `btrfs_insert_one_raid_extent()`, `btrfs_get_raid_extent_offset()`, and `btrfs_delete_raid_extent()`.

## Main Entry Point

- `btrfs_test_raid_stripe_tree(u32 sectorsize, u32 nodesize)`: runs each test in the `tests[]` table through `run_test()`.

## Harness

`run_test()`:
- Allocates dummy `fs_info`.
- Allocates a dummy root and marks it as `BTRFS_RAID_STRIPE_TREE_OBJECTID`.
- Enables `BTRFS_FEATURE_INCOMPAT_RAID_STRIPE_TREE`.
- Sets `fs_info->stripe_root` and `tree_root`.
- Allocates an empty leaf extent buffer.
- Allocates two dummy devices with devids `0` and `1`.
- Initializes a dummy transaction and invokes the specific test.

`btrfs_device_by_devid()` searches the dummy device list.

The fixed profile is a two-device RAID1 data mapping:
`BTRFS_BLOCK_GROUP_DATA | BTRFS_BLOCK_GROUP_RAID1`.

## Test Scenarios

- `test_simple_create_delete()`: inserts one 64 KiB RAID1 stripe extent at logical 1 MiB, verifies lookup on device 0, then deletes it.
- `test_create_update_delete()`: inserts the same logical range twice with shifted physical addresses, verifying that reinsert updates the existing stripe item.
- `test_tail_delete()`: deletes the final 16 KiB of a 64 KiB extent and verifies a 48 KiB front segment remains.
- `test_front_delete()`: deletes the first 16 KiB of a 64 KiB extent and verifies the remaining item starts at logical/physical `1 MiB + 16 KiB`.
- `test_front_delete_prev_item()`: inserts two adjacent 1 MiB extents, deletes a range spanning the tail of the first and head of the second, and verifies truncation plus a hole.
- `test_punch_hole()`: deletes a 64 KiB middle range from one 1 MiB extent and verifies two surviving extents around the hole.
- `test_punch_hole_3extents()`: inserts three adjacent 1 MiB extents and deletes a 2 MiB middle range, validating first-item truncation, middle deletion, and third-item front truncation.
- `test_delete_two_extents()`: inserts three adjacent 1 MiB extents, deletes the first two, verifies lookups fail for the deleted ranges, and verifies the third remains intact.

## Key Dependencies

- RAID stripe tree API from `raid-stripe-tree.h`.
- IO context allocation and stripe mapping structures from Btrfs volume code.
- Dummy fs/root/device helpers from the Btrfs selftest framework.
- Real B-tree insert/delete/search behavior through `stripe_root`.

## Important Invariants

- Each inserted `bioc` has `map_type`, `size`, `logical`, and per-stripe device/physical addresses initialized.
- Device 0 is commonly used for lookup verification through `io_stripe.dev`.
- Surviving mappings are checked for both physical offset and returned length.
- Deleted/hole ranges are expected to return `-ENODATA`.
- Tests clean up inserted extents where possible so each scenario remains isolated in its fresh dummy fs.

## Error Handling

Tests return:
- `-ENOMEM` for allocation failures.
- `-EINVAL` for unexpected physical addresses, lengths, or lookup outcomes.
- The underlying Btrfs API error for insert/delete/lookup failures.

## Research Notes

The file is intentionally repetitive. The duplicated setup makes each logical/physical range expectation explicit, which is useful for validating stripe tree split/truncate/delete behavior without hiding details behind test helpers.
