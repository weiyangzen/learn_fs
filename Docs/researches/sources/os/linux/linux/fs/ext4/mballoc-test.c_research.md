# File Research: sources/os/linux/linux/fs/ext4/mballoc-test.c

## Purpose

`mballoc-test.c` is a KUnit test module for ext4 multiblock allocation internals. It builds a lightweight synthetic ext4 superblock, group descriptors, and block bitmaps, stubs selected ext4 metadata accessors, and verifies allocator behavior for simple allocation/free paths, buddy generation, buddy mark/free operations, diskspace marking, and a slow-path cost measurement.

## Test Harness Structures

- `struct mbt_grp_ctx` stores one synthetic group context:
  - a bitmap buffer head.
  - a placeholder ext4 group descriptor.
  - a placeholder group-descriptor buffer head.
- `struct mbt_ctx` owns the array of group contexts.
- `struct mbt_ext4_super_block` embeds:
  - an on-disk `struct ext4_super_block`.
  - an in-memory `struct ext4_sb_info`.
  - the test-only group context.
- `struct mbt_ext4_block_layout` parameterizes block size, cluster bits, blocks per group, group count, and descriptor size.
- `struct test_range` represents a generated group-local start/length pair.

The `MBT_SB`, `MBT_CTX`, and `MBT_GRP_CTX` macros recover test harness state from a kernel `struct super_block`.

## Synthetic Superblock and mballoc Setup

- `mbt_alloc_inode()` allocates `struct ext4_inode_info`, initializes ext4 inode locks/state, and returns its VFS inode.
- `mbt_free_inode()` frees the ext4 inode wrapper.
- `mbt_sops`, `mbt_kill_sb()`, `mbt_init_fs_context()`, `mbt_fs_type`, and `mbt_set()` provide enough filesystem scaffolding for `sget_fc()` and `generic_shutdown_super()`.
- `mbt_ext4_alloc_super_block()` allocates the combined test superblock object, obtains a kernel `super_block`, initializes the ext4 blockgroup lock, wires `s_fs_info`, and releases the mount semaphore.
- `mbt_ext4_free_super_block()` frees the blockgroup lock, deactivates the superblock, and releases the wrapper object.
- `mbt_init_sb_layout()` fills ext4 geometry fields from the current test parameter.
- `mbt_mb_init()` allocates a fake block device and request queue, initializes `s_inodes` and super operations, calls `ext4_mb_init()`, and initializes free/dirty cluster percpu counters.
- `mbt_mb_release()` tears down percpu counters, mballoc state, and fake block-device memory.

## Group Bitmap Context

- `mbt_grp_ctx_init()` allocates a zeroed block bitmap, marks bits beyond the valid cluster count as used, and initializes the descriptor free-cluster count.
- `mbt_ctx_init()` allocates all group contexts after layout setup, initializes every group bitmap, and marks the first data cluster in group 0 as used so allocator tests do not select an invalid first filesystem block.
- `mbt_ctx_release()` releases all synthetic group bitmaps.
- `mbt_ctx_mark_used()` marks a range used in a chosen group bitmap.
- `mbt_ctx_bitmap()` returns a raw bitmap pointer for assertions and expected-state generation.

## Static Stubs

KUnit static stubs replace selected ext4 functions while tests run:

- `ext4_read_block_bitmap_nowait_stub()` returns the synthetic group bitmap buffer and increments its buffer-head reference count.
- `ext4_wait_block_bitmap_stub()` marks the synthetic bitmap buffer as uptodate, bitmap-uptodate, and verified.
- `ext4_get_group_desc_stub()` returns the synthetic group descriptor and optional descriptor buffer head.
- `ext4_mb_mark_context_stub()` mutates the synthetic bitmap for mark/free calls without doing real journal or metadata IO.

`mbt_kunit_init()` allocates the synthetic superblock, applies the current layout parameter, initializes group contexts, activates these static stubs, initializes mballoc, and stores the superblock in `test->priv`. `mbt_kunit_exit()` releases mballoc state, group contexts, and the superblock.

## Allocation and Free Tests

- `test_new_blocks_simple()` validates `ext4_mb_new_blocks_simple_test()`:
  - allocation exactly at a free goal.
  - next allocation after the same goal.
  - fallback to the next group when the goal group is full.
  - fallback to an earlier group when later groups are full.
  - error reporting when no blocks are available.
- `mbt_generate_test_ranges()` creates per-test ranges spread across a group.
- `validate_free_blocks_simple()` verifies that only the expected group and expected range became free.
- `test_free_blocks_simple_range()` frees one range through `ext4_free_blocks_simple_test()` and validates bitmap state.
- `test_free_blocks_simple()` fills all groups, generates ranges, and tests simple free behavior in the goal group.
- `test_mark_diskspace_used_range()` validates that `ext4_mb_mark_diskspace_used_test()` marks exactly the requested range.
- `test_mark_diskspace_used()` runs diskspace marking across generated ranges.

## Buddy Generation and Mutation Tests

- `mbt_generate_buddy()` independently builds the expected mballoc buddy bitmap and group statistics from a raw block bitmap. It computes first free cluster, free counts, buddy counters by order, largest free order, and fragment count.
- `mbt_validate_group_info()` compares key `struct ext4_group_info` fields and buddy counters.
- `do_test_generate_buddy()` compares independently generated buddy state against `ext4_mb_generate_buddy_test()`.
- `test_mb_generate_buddy()` allocates scratch bitmaps/group-info state, progressively marks generated used ranges, and validates ext4 buddy generation after each change.
- `test_mb_mark_used_range()` calls `mb_mark_used_test()` under the group lock, updates an independent bitmap, regenerates expected buddy state, and compares it with the loaded ext4 buddy.
- `test_mb_mark_used()` loads a buddy for the goal group and validates repeated mark-used operations.
- `test_mb_free_blocks_range()` calls `mb_free_blocks_test()` under the group lock, updates an independent bitmap, regenerates expected buddy state, and compares it with the loaded ext4 buddy.
- `test_mb_free_blocks()` first marks the entire group used, then validates repeated free operations against expected buddy state.

Buddy-cache tests skip layouts where the filesystem block size exceeds `PAGE_SIZE`, because the buddy cache assumes each page contains at least one block.

## Cost Measurement

`test_mb_mark_used_cost()` is marked `KUNIT_SPEED_SLOW`. It repeatedly generates ranges, times `mb_mark_used_test()` loops using `jiffies`, frees the same ranges, totals elapsed jiffies across `COUNT_FOR_ESTIMATE` iterations, and reports the cost with `kunit_info()`. This is an observational performance test rather than a strict correctness assertion.

## Test Parameters and Suite Registration

`mbt_test_layouts` defines three layouts:

- 1 KiB blocks, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.
- 4 KiB blocks, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.
- 64 KiB blocks, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.

`KUNIT_ARRAY_PARAM()` exposes these layouts to every test case. `mbt_test_cases` registers parameterized correctness tests plus the slow cost test. `mbt_test_suite` names the suite `ext4_mballoc_test`, attaches init/exit hooks, and `kunit_test_suites()` registers it as a GPL module.

## Dependencies

This file depends on KUnit, KUnit static stubs, Linux filesystem context helpers, random number generation, ext4 core definitions, and `mballoc.h` internals. It intentionally calls test-visible ext4 allocator functions such as `ext4_mb_new_blocks_simple_test()`, `ext4_free_blocks_simple_test()`, `ext4_mb_mark_diskspace_used_test()`, `ext4_mb_generate_buddy_test()`, `mb_mark_used_test()`, `mb_free_blocks_test()`, `ext4_mb_load_buddy_test()`, and `ext4_mb_unload_buddy_test()`.

## Research Notes

The test design avoids real disk IO by replacing bitmap and group-descriptor access with synthetic in-memory state, while still exercising ext4's actual mballoc logic. The strongest correctness pattern is dual implementation: tests build expected buddy/bitmap/group-info state independently and then compare it against ext4-generated state. The random range generator broadens coverage within each layout, but the suite remains deterministic only to the extent that KUnit/kernel random behavior is controlled by the test environment.
