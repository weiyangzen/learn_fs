# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/raid-stripe-tree-tests.c

## Role

Self-tests for RAID stripe tree insert, lookup, update, and deletion behavior. Each test creates a fresh dummy filesystem with the `RAID_STRIPE_TREE` incompat feature, a dummy stripe root, and two dummy devices.

## Main Entry Point

- `btrfs_test_raid_stripe_tree(sectorsize, nodesize)`: iterates a table of test functions and runs each through `run_test()`.

## Test Harness

- `run_test()`: builds dummy `fs_info`, root, empty leaf node, and two devices with devids `0` and `1`, then creates a dummy transaction.
- `btrfs_device_by_devid()`: local device lookup helper over `fs_devices->devices`.

## Covered Behaviors

- `test_simple_create_delete()`: inserts one RAID1 stripe extent, verifies physical mapping and length, then deletes it.
- `test_create_update_delete()`: overwrites an existing stripe extent with new physical addresses to exercise update behavior inside `btrfs_insert_one_raid_extent()`.
- `test_tail_delete()`: truncates the tail of an extent and verifies the remaining prefix plus hole lookup.
- `test_front_delete()`: deletes from the front and verifies the item start/physical offset moves forward.
- `test_front_delete_prev_item()`: deletes a range spanning two adjacent on-disk stripe items and verifies the first is truncated, the second is shifted, and the removed middle is absent.
- `test_punch_hole()`: deletes a middle range from a single extent and verifies two remaining fragments.
- `test_punch_hole_3extents()`: deletes a range spanning three extents, checking dropped middle extent plus trimmed bookends.
- `test_delete_two_extents()`: removes two whole extents while preserving the third.

## Dependencies and Interactions

- Calls production RAID stripe tree APIs: `btrfs_insert_one_raid_extent()`, `btrfs_delete_raid_extent()`, and `btrfs_get_raid_extent_offset()`.
- Uses `alloc_btrfs_io_context()` and `btrfs_io_stripe` to model logical-to-physical stripe layout.
- Assumes two-device RAID1 through `RST_TEST_RAID1_TYPE`.

## Error Handling Notes

- Expected absent ranges return `-ENODATA`; any successful lookup in a hole is treated as test failure.
- Each test cleans up inserted stripe extents where possible and releases the `bioc`.
