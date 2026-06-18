# File Research: sources/os/linux/linux-stable/fs/ext4/mballoc-test.c

## Summary
KUnit test suite for ext4 multiblock allocation internals. It builds a synthetic ext4 superblock and per-group bitmap/descriptor context, stubs selected ext4 bitmap and group-descriptor functions, initializes the real mballoc backend, and tests allocation, freeing, buddy generation, buddy mutation, diskspace marking, and mark-used cost behavior across several block and cluster layouts.

## Main Responsibilities
- Creates a minimal ext4 mount environment sufficient for `ext4_mb_init()` and mballoc test helpers.
- Provides synthetic per-group bitmap buffers and group descriptors.
- Stubs block bitmap reads, bitmap wait/verification, group descriptor lookup, and bitmap-marking context updates.
- Runs parameterized KUnit tests over multiple block-size layouts.
- Validates mballoc bitmap and buddy-cache state against independently generated expected state.
- Includes a slow cost-estimation test for repeated `mb_mark_used()` / `mb_free_blocks()` cycles.

## Test Fixture and Synthetic Filesystem
The fixture wraps ext4 state in:
- `struct mbt_ext4_super_block`, containing an on-disk superblock image, `struct ext4_sb_info`, and private test context.
- `struct mbt_ctx`, holding an array of per-group contexts.
- `struct mbt_grp_ctx`, holding a bitmap buffer head, group descriptor, and placeholder descriptor buffer head.

`mbt_ext4_alloc_super_block()` allocates this wrapper, obtains a VFS superblock with `sget()`, allocates and initializes ext4 block-group locking, wires `s_es`, `s_sb`, and `s_fs_info`, and drops the superblock umount lock. `mbt_ext4_free_super_block()` frees the block-group lock, deactivates the superblock, and frees the wrapper.

`mbt_init_sb_layout()` configures VFS block size, ext4 group count, blocks per group, cluster bits/ratio, clusters per group, descriptor size, descriptor-per-block values, first data block, and total block count from a parameterized layout.

`mbt_ctx_init()` allocates one group context per group, initializes each bitmap to free clusters plus any out-of-range bits marked used, sets group free-cluster counts, and marks the first cluster of group 0 used to avoid allocating the filesystem's first data block in ways that would fail block-validity checks.

`mbt_mb_init()` creates a fake block device and request queue, initializes `s_inodes` and `s_op`, calls real `ext4_mb_init()`, initializes free and dirty cluster percpu counters, and unwinds all resources on failure. `mbt_mb_release()` destroys counters, releases mballoc state, and frees fake block-device objects.

## Static Stubs
The suite uses KUnit static stubs for controlled I/O-free behavior:
- `ext4_read_block_bitmap_nowait_stub()` returns the synthetic group bitmap buffer and increments its buffer-head refcount to match caller expectations.
- `ext4_wait_block_bitmap_stub()` marks the bitmap buffer uptodate, bitmap-uptodate, and verified.
- `ext4_get_group_desc_stub()` returns the synthetic descriptor and optional placeholder descriptor buffer.
- `ext4_mb_mark_context_stub()` applies set/clear operations directly to the synthetic bitmap.

These stubs let real mballoc helper code run without disk I/O or real group descriptor blocks.

## Test Cases
`test_new_blocks_simple()` verifies `ext4_mb_new_blocks_simple_test()`:
- Allocates at the requested goal block.
- Allocates the next cluster after the goal when the goal is already used.
- Falls forward to the next group when the goal group is full.
- Falls back to earlier groups when later groups are full.
- Fails when no clusters remain available.

`test_free_blocks_simple()` marks all groups used, generates random non-overlapping-ish test ranges, frees ranges in the goal group through `ext4_free_blocks_simple_test()`, then validates that only the expected goal-group range is free and all other groups remain fully used.

`test_mark_diskspace_used()` builds an `ext4_allocation_context`, runs `ext4_mb_mark_diskspace_used_test()` for generated ranges, and checks that the bitmap contains exactly one used range at the expected start and length.

`test_mb_generate_buddy()` compares ext4's `ext4_mb_generate_buddy_test()` output against an independent local buddy generator. It validates both the raw buddy bitmap memory and `struct ext4_group_info` fields such as first free cluster, fragment count, free count, largest free order, and per-order counters.

`test_mb_mark_used()` loads a real ext4 buddy for the goal group, applies generated ranges through `mb_mark_used_test()` under the group lock, mirrors the same changes into an expected bitmap, regenerates the expected buddy, and compares the resulting buddy memory and group info.

`test_mb_free_blocks()` first marks an entire buddy group used, then frees generated ranges through `mb_free_blocks_test()` under the group lock, mirrors the clear operations into an expected bitmap, regenerates the expected buddy, and compares state.

`test_mb_mark_used_cost()` is marked slow. It loads a buddy, repeatedly generates ranges for `COUNT_FOR_ESTIMATE` iterations, measures jiffies spent marking ranges used, frees them again each iteration, and emits the accumulated cost with `kunit_info()`.

## Independent Buddy Generator
`mbt_generate_buddy()` derives expected buddy-cache state from a bitmap:
- Starts with all buddy bits set.
- Finds free bits in the original bitmap and records order-0 counters and free count.
- Coalesces adjacent free pairs into higher-order buddy levels by clearing bits in higher-level buddy maps and adjusting per-order counters.
- Tracks largest free order.
- Counts free fragments by scanning transitions from free to used and back.

`mbt_validate_group_info()` compares generated and ext4-produced group-info metadata. `do_test_generate_buddy()` runs both the local generator and ext4 generator and asserts exact memory equality for the buddy buffer.

## Parameterization
The suite defines three layouts:
- 1 KiB block size, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.
- 4 KiB block size, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.
- 64 KiB block size, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.

`mbt_show_layout()` formats these parameters for KUnit output. Tests that rely on buddy pages skip when filesystem block size exceeds `PAGE_SIZE`, because the buddy cache assumes each page contains at least one block.

## Dependencies
Depends on KUnit, KUnit static stubs, Linux random helpers, ext4 core definitions, and `mballoc.h` test-visible helper symbols such as `ext4_mb_new_blocks_simple_test()`, `ext4_free_blocks_simple_test()`, `ext4_mb_mark_diskspace_used_test()`, `ext4_mb_generate_buddy_test()`, `ext4_mb_load_buddy_test()`, `ext4_mb_unload_buddy_test()`, `mb_mark_used_test()`, and `mb_free_blocks_test()`.

## Risks and Test Limitations
The suite exercises allocator internals without real disk I/O, journal transactions, real block devices, or full mount setup. Random range generation broadens coverage but can make exact scenario reproduction depend on KUnit/random state. The independent buddy generator is useful as an oracle, but it must remain semantically aligned with ext4's buddy invariants. The 64 KiB layout is included, but buddy-cache mutation tests skip when block size exceeds page size.
