# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/raid-stripe-tree-tests.c

## Purpose

This file implements Btrfs selftests for RAID stripe tree operations. It builds dummy filesystems with a `stripe_root`, synthetic devices, and dummy transactions, then verifies insertion, lookup, update, and deletion behavior for RAID stripe extents.

The tests focus on how `btrfs_insert_one_raid_extent()`, `btrfs_get_raid_extent_offset()`, and `btrfs_delete_raid_extent()` handle exact deletes, front/tail truncation, hole punching, item updates, and ranges spanning adjacent stripe tree items.

## Main Entry Point

- `btrfs_test_raid_stripe_tree(u32 sectorsize, u32 nodesize)`: runs every function in the `tests[]` table through `run_test()`.

## Test Harness

- `run_test(test_func_t test, u32 sectorsize, u32 nodesize)`:
  - Allocates dummy `fs_info`.
  - Allocates a dummy root and marks it as `BTRFS_RAID_STRIPE_TREE_OBJECTID`.
  - Enables `BTRFS_FEATURE_INCOMPAT_RAID_STRIPE_TREE`.
  - Sets `fs_info->stripe_root` and `tree_root`.
  - Allocates a leaf extent buffer for the root.
  - Allocates two dummy devices with devids `0` and `1`.
  - Initializes a dummy transaction and runs the supplied test.

- `btrfs_device_by_devid()`: local helper that searches the dummy device list for a requested devid.

## Covered Scenarios

- `test_simple_create_delete()`:
  - Inserts one 64 KiB RAID1 stripe extent at logical 1 MiB.
  - Verifies lookup returns the physical address on device 0 and length 64 KiB.
  - Deletes the extent.

- `test_create_update_delete()`:
  - Inserts a 64 KiB extent.
  - Re-inserts the same logical range with shifted physical addresses.
  - Verifies lookup reflects the updated physical mapping.
  - Deletes the updated extent.
  - Explicitly exercises update behavior inside `btrfs_insert_one_raid_extent()`.

- `test_tail_delete()`:
  - Inserts a 64 KiB extent.
  - Deletes the final 16 KiB.
  - Verifies the remaining front extent is 48 KiB and the deleted tail is absent.

- `test_front_delete()`:
  - Inserts a 64 KiB extent.
  - Deletes the first 16 KiB.
  - Verifies the remaining stripe starts at logical/physical `1 MiB + 16 KiB`, has length 48 KiB, and the deleted front range is absent.

- `test_front_delete_prev_item()`:
  - Inserts two adjacent 1 MiB items.
  - Deletes a 1 MiB range starting halfway through the first item.
  - Verifies the first item is truncated to 512 KiB, the second item’s surviving part starts 512 KiB later, and the hole lookup fails.

- `test_punch_hole()`:
  - Inserts one 1 MiB extent.
  - Deletes a 64 KiB middle range.
  - Verifies two surviving extents around the hole and absence of the hole.

- `test_punch_hole_3extents()`:
  - Inserts three adjacent 1 MiB extents.
  - Deletes a 2 MiB range beginning 256 KiB into the first extent.
  - Verifies first item truncation, second item removal, third item front truncation, and cleanup deletion of survivors.

- `test_delete_two_extents()`:
  - Inserts three adjacent 1 MiB extents.
  - Deletes the first two.
  - Verifies the first two lookups return `-ENODATA`, while the third remains intact.

## Dependencies and Integration

The test uses:
- RAID stripe tree API from `raid-stripe-tree.h`.
- IO context allocation from Btrfs volume/mapping code.
- Dummy fs/root/device helpers from the selftest framework.
- Real B-tree insertion/deletion/search through the stripe root.

The fixed test configuration uses:
- Two devices.
- RAID1 data profile: `BTRFS_BLOCK_GROUP_DATA | BTRFS_BLOCK_GROUP_RAID1`.
- Device physical placement offset by 1 GiB per device.

## Important Invariants

- Every test must assign `bioc->map_type`, `bioc->size`, `bioc->logical`, and each stripe’s `dev`/`physical` before insertion.
- Lookup checks are usually performed against device 0 by setting `io_stripe.dev`.
- Deletion tests validate both positive surviving mappings and negative lookups for holes/deleted ranges.
- Each test cleans up inserted extents before returning where possible, so independent tests can run in fresh dummy fs contexts.

## Error Handling

Each test reports mismatch details via `test_err()` and returns:
- `-ENOMEM` for allocation failures.
- `-EINVAL` for unexpected lookup success/failure or wrong physical/length results.
- The original Btrfs API return code for insertion/deletion/lookup failures.

## Research Notes

The tests are intentionally explicit and repetitive. That makes individual stripe-tree edge cases easy to inspect and avoids hiding the exact logical/physical range expectations behind helper abstractions.
