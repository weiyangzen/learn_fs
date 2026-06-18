# File Research: sources/os/linux/linux/fs/ext4/extents-test.c

## Purpose

`extents-test.c` is a KUnit test module for ext4 extent split and conversion behavior. It verifies direct extent split/convert logic and higher-level map/create paths, including fallback zeroout behavior when extent insertion fails.

## Test Subject

The tests focus on behavior around:

- `ext4_split_convert_extents()`, exposed to tests as `ext4_split_convert_extents_test()`.
- `ext4_map_query_blocks()`.
- `ext4_map_create_blocks()`.
- conversion from unwritten to written extents.
- conversion from written to unwritten extents.
- zeroout fallback when split insertion fails with `-ENOSPC`.
- extent status cache synchronization for higher-level paths.

## Fixed Test Geometry

- `EXT_DATA_PBLK = 100`
- `EXT_DATA_LBLK = 10`
- `EXT_DATA_LEN = 3`
- Block size is configured as 4096 bytes.
- Each test starts with one extent covering logical blocks `[10, 13)` and physical blocks `[100, 103)`.
- The extent may start as written or unwritten depending on test parameters.

## Test Context

- `struct kunit_ctx`
  - Holds a mocked `ext4_inode_info`.
  - Holds `k_data`, a memory buffer simulating disk data for zeroout tests.

- `struct kunit_ext_state`
  - Expected logical block, length, and unwritten state for resulting extents.

- `struct kunit_ext_data_state`
  - Expected character value and block range in the simulated data buffer.

- `struct kunit_ext_test_param`
  - Parameterizes all test variants:
    - description
    - test type
    - initial unwritten state
    - split flags
    - split map
    - zeroout enable/disable
    - expected extent count
    - expected extent states
    - expected data buffer segments for zeroout tests

## Mock Filesystem Setup

- Defines a minimal `file_system_type` named `"extents test"`.
- `extents_kunit_init()`:
  - Allocates `ext4_sb_info`.
  - Creates a superblock through `fs_context_for_mount()` and `sget_fc()`.
  - Sets ext4 private superblock state.
  - Sets block size and block size bits.
  - Enables zeroout threshold unless disabled by the test parameter.
  - Registers the extent status shrinker.
  - Allocates a mock `ext4_inode_info`.
  - Initializes the inode extent status tree and locks.
  - Marks the inode as extent-based.
  - Allocates `k_data` and fills it with `'X'`.
  - Constructs a depth-zero extent tree directly in `i_data`.
  - Inserts the matching extent status cache entry.
  - Activates static stubs for dirtying and zeroout.

- `extents_kunit_exit()`:
  - Unregisters the extent status shrinker.
  - Deactivates the superblock.
  - Frees superblock private state, inode state, and data buffer.

## Static Stubs

- `__ext4_ext_dirty_stub()`
  - Returns success without journaling.

- `ext4_ext_insert_extent_stub()`
  - Returns `ERR_PTR(-ENOSPC)` to force zeroout fallback.

- `ext4_ext_zeroout_stub()`
  - Validates the requested extent is within the fixed test extent.
  - Zeroes the corresponding range in `k_data`.

- `ext4_issue_zeroout_stub()`
  - Validates logical and physical offsets line up.
  - Zeroes the corresponding range in `k_data`.

## Test Execution

- `check_buffer()`
  - Verifies that a buffer range is filled with one expected byte.
  - Logs first mismatch.

- `ext4_map_create_blocks_helper()`
  - Calls `ext4_map_query_blocks()` to populate map flags and physical block information.
  - Calls `ext4_map_create_blocks()` to trigger split/conversion.
  - Used instead of full `ext4_map_blocks()` to avoid mocking unrelated code.

- `test_split_convert()`
  - Shared test body for all parameter sets.
  - Optionally stubs `ext4_ext_insert_extent()` to force zeroout fallback.
  - Finds the initial extent and validates starting state.
  - Runs either:
    - direct `ext4_split_convert_extents_test()`, or
    - high-level query/create block path.
  - Re-reads the extent tree and compares every expected extent.
  - For high-level paths, verifies extent status cache contains corresponding written/unwritten status and physical block.
  - For zeroout tests, validates simulated data buffer segments.

## Parameter Groups

- `test_split_convert_params`
  - Direct split/convert tests.
  - Covers:
    - unwritten to written conversion for first half, second half, and middle.
    - written to unwritten conversion for first half, second half, and middle.
    - zeroout fallback for the same variants.
  - Direct split tests ignore extent status cache checks because the split function uses `EXT4_EX_NOCACHE`.

- `test_convert_initialized_params`
  - High-level tests for the `ext4_ext_map_blocks() -> convert_initialized_extent()` path.
  - Covers written-to-unwritten conversion with normal split and zeroout fallback.

- `test_handle_unwritten_params`
  - High-level tests for the `ext4_ext_map_blocks() -> ext4_ext_handle_unwritten_extents()` path.
  - Covers:
    - unwritten-to-written conversion via endio-style `EXT4_GET_BLOCKS_CONVERT`.
    - unwritten-to-written conversion via non-endio `EXT4_GET_BLOCKS_CREATE`.
    - zeroout fallback for both paths.
    - non-zeroout split behavior with zeroout disabled.

## KUnit Registration

- Uses `KUNIT_CASE_PARAM_WITH_INIT()` instead of the more compact array macro because of noted output parsing limitations.
- Registers three parameterized invocations of `test_split_convert()`.
- Suite name: `ext4_extents_test`.
- Module license: GPL.

## Dependencies

- KUnit framework and static stubs.
- Minimal VFS superblock/context helpers.
- ext4 core header and extents header.
- Extent status tree functions.
- Test-only exports enabled by `CONFIG_EXT4_KUNIT_TESTS`.

## Research Notes

This test is focused and synthetic. It does not mount a real ext4 filesystem; instead, it builds the minimum inode/superblock/extent-status state needed to exercise extent split and conversion code. The simulated data buffer is important because it verifies not only tree shape but also zeroout correctness, preventing fallback conversion from leaking stale bytes.
