# sources/test-tools/xfstests/tests/generic/391

## Purpose
Test two threads doing non-overlapping direct I/O in the same extents. Motivated by a bug in Btrfs' direct I/O get_block function which would lead to spurious -EEXIST failures from direct I/O reads. It is registered as generic/391 with `_begin_fstest` tags `auto, quick, rw, prealloc`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include extent_size=$(($(_get_block_size "$TEST_DIR") * 2)), num_extents=1024, testfile=$TEST_DIR/$$-testfile. Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command "falloc"; _require_test_program "dio-interleaved"; _require_odirect.

External/helper commands: $XFS_IO_PROG, rm, truncate.

Representative `xfs_io` operations: falloc $off $extent_size.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
