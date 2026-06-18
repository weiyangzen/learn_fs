# sources/test-tools/xfstests/tests/generic/469

## Purpose
Test that mmap read doesn't see non-zero data past EOF on truncate down. This is inspired by an XFS bug that truncate down fails to zero page cache beyond new EOF and causes stale data written to disk unexpectedly and a subsequent mmap reads and sees non-zeros post EOF. Patch "xfs: truncate pagecache before writeback in xfs_setattr_size()" fixed the bug on XFS. It is registered as generic/469 with `_begin_fstest` tags `auto, quick, punch, zero, prealloc, mmap`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, run_fsx, test_fsx. Important state variables and paths include file=$TEST_DIR/$seq.fsx. Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup, run_fsx, test_fsx.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command "falloc" "-k"; _require_xfs_io_command "fpunch"; _require_xfs_io_command "fzero".

External/helper commands: $FSX_PROG, fallocate, fsx, rm, truncate.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: fsx --replay-ops fsxops.0; fsx -y --replay-ops fsxops.0; fsx --replay-ops fsxops.1; fsx -y --replay-ops fsxops.1; fsx --replay-ops fsxops.2; fsx -y --replay-ops fsxops.2. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
