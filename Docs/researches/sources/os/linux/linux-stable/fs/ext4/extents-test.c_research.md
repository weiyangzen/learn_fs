# File Research: sources/os/linux/linux-stable/fs/ext4/extents-test.c

## Summary
KUnit test suite for ext4 extent split and conversion behavior. It constructs a minimal ext4 inode with one three-block extent, stubs selected extent and zeroout operations, then validates direct split/convert paths and higher-level `ext4_map_create_blocks()` paths for written-to-unwritten, unwritten-to-written, and zeroout fallback cases.

## Main Responsibilities
- Creates a synthetic superblock, `ext4_sb_info`, and `ext4_inode_info` suitable for extent tests.
- Builds a depth-0 extent tree rooted in the inode's `i_data`.
- Initializes the extent status tree and verifies it for high-level map-create tests.
- Provides KUnit static stubs for extent dirtying, forced insert failure, extent zeroout, and block zeroout.
- Exercises `ext4_split_convert_extents_test()` directly.
- Exercises `ext4_map_query_blocks()` plus `ext4_map_create_blocks()` for high-level initialized and unwritten conversion paths.
- Verifies final extent layout, unwritten flags, physical block mapping, extent status cache state, and zeroed data-buffer regions.

## Test Fixture
The fixture uses:
- `EXT_DATA_LBLK = 10`.
- `EXT_DATA_PBLK = 100`.
- `EXT_DATA_LEN = 3`.
- 4 KiB block size.
- One inode extent covering logical blocks `[10, 13)` and physical blocks `[100, 103)`.
- A separate three-block `k_data` buffer initialized with `X` to model underlying disk data for zeroout validation.

`extents_kunit_init()` allocates the mount/inode objects, registers the extent status shrinker, marks the inode as extents-based, configures optional zeroout, builds the initial extent header and extent, inserts the matching extent status entry, and activates common stubs. `extents_kunit_exit()` unregisters shrinker state, deactivates the synthetic superblock, and frees fixture allocations.

## Important Helpers
- `ext4_ext_insert_extent_stub()` returns `-ENOSPC` to force zeroout fallback.
- `ext4_ext_zeroout_stub()` zeroes the modeled data buffer for a whole extent.
- `ext4_issue_zeroout_stub()` zeroes the modeled data buffer for a logical/physical range and checks that logical and physical offsets match.
- `ext4_map_create_blocks_helper()` calls `ext4_map_query_blocks()` first to populate map flags and physical block data, then calls `ext4_map_create_blocks()`.
- `test_split_convert()` performs initial assertions, invokes the selected test path, verifies expected extents, optionally checks the extent status cache, and optionally verifies modeled zeroout results.

## Parameter Coverage
`test_split_convert_params` covers direct split/convert behavior:
- Unwritten to written conversion at the beginning, end, and middle of the extent.
- Written to unwritten conversion at the beginning, end, and middle.
- Zeroout fallback for the same split shapes, expecting one fully written extent and selective zeroing of regions outside or inside the requested split.

`test_convert_initialized_params` covers high-level conversion of initialized extents to unwritten through `ext4_map_create_blocks()`, including normal split and zeroout fallback cases.

`test_handle_unwritten_params` covers high-level handling of unwritten extents becoming written through end-I/O-style `EXT4_GET_BLOCKS_CONVERT` and non-end-I/O `EXT4_GET_BLOCKS_CREATE` paths, with and without zeroout fallback.

## KUnit Registration
The suite is named `ext4_extents_test`. It registers three parameterized cases using `KUNIT_CASE_PARAM_WITH_INIT()` because the file notes parsing limitations in the compact `KUNIT_ARRAY_PARAM()` form. The test module declares GPL licensing.

## Dependencies
Depends on KUnit, static stubs, ext4 core definitions, extent tree helpers, extent status helpers, and KUnit-only test exports from `ext4_extents.h` / `extents.c`.

## Risks
The fixture intentionally mocks only a narrow slice of ext4, so it is strong for extent split/conversion invariants but not a full integration test of journaling, allocation, writeback, or real block I/O. Global `k_ctx` means tests assume KUnit's fixture lifecycle isolates cases correctly. The expected zeroout matrix is sensitive to exact fallback semantics in extent conversion code.
