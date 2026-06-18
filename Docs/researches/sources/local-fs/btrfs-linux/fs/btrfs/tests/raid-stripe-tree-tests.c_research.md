# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/raid-stripe-tree-tests.c

## Summary
Selftests RAID stripe tree insert, update, lookup, and deletion behavior for a synthetic two-device RAID1 filesystem.

## Main Responsibilities
- Allocate dummy fs/device/stripe-root state with `RAID_STRIPE_TREE` incompat enabled.
- Insert RAID stripe extents through `btrfs_insert_one_raid_extent()`.
- Delete full, front, tail, middle, and multi-item ranges through `btrfs_delete_raid_extent()`.
- Verify logical-to-physical mapping and surviving lengths with `btrfs_get_raid_extent_offset()`.
- Run each scenario in a fresh dummy transaction/filesystem.

## Key APIs
- Test entry: `btrfs_test_raid_stripe_tree()`.
- Harness: `run_test()`, `btrfs_device_by_devid()`.
- Test cases: `test_simple_create_delete()`, `test_create_update_delete()`, `test_tail_delete()`, `test_front_delete()`, `test_front_delete_prev_item()`, `test_punch_hole()`, `test_punch_hole_3extents()`, `test_delete_two_extents()`.

## Important Behavior
The simple create/delete case writes a 64K RAID1 stripe extent at logical 1M, with device 0 physical at 1M and device 1 physical at 1G+1M, verifies lookup, then deletes it.

The update case overwrites the same logical range with new physical addresses offset by 1G, exercising update-in-place behavior in RAID stripe extent insertion.

Tail and front delete cases truncate a single 64K item from either end and verify both the surviving mapping and the deleted hole.

`test_front_delete_prev_item()` inserts adjacent 1M items, deletes a range starting halfway through the first and continuing into the second, then verifies the first item is shortened, the second item starts later, and the middle range is absent.

Punch-hole tests split one or several extents around deleted middle ranges. The three-extent case verifies deletion of all middle extents plus partial trimming of both bookends.

`test_delete_two_extents()` removes the first two of three adjacent extents and verifies the third remains unchanged.

## Setup and State
Each scenario gets a new dummy `fs_info`, root, leaf extent buffer, and two dummy devices with devids `0` and `1`. The stripe root is both `fs_info->stripe_root` and `tree_root` for the dummy btree operations.

## Risks
The file is scenario-heavy and sensitive to exact length/offset expectations. Several cleanup paths delete surviving extents after verification, so a failed intermediate assertion may leave dummy tree state unclean only within that isolated test instance.
