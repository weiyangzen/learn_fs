# sources/test-tools/xfstests/tests/generic/485

## Purpose
Regression test for: 349fa7d6e193 ("ext4: prevent right-shifting extents beyond EXT_MAX_BLOCKS") 7d83fb14258b ("xfs: prevent creating negative-sized file via INSERT_RANGE"). It is registered as generic/485 with `_begin_fstest` tags `auto, quick, insert, prealloc`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include block_size=$(_get_file_block_size $TEST_DIR), max_file_size=$(_get_max_file_size $TEST_DIR), max_blocks=$((max_file_size / block_size)), testfile=$TEST_DIR/testfile.$seq. Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_math; _require_xfs_io_command "falloc" "-k"; _require_xfs_io_command "finsert"; _require_xfs_io_command "truncate".

External/helper commands: $XFS_IO_PROG, rm, truncate.

Representative `xfs_io` operations: falloc 0 $((2 * block_size)); falloc -k $(( (max_blocks - 1) * $block_size )) $block_size; finsert 0 $((2 * block_size)); falloc $(( (max_blocks - 1) * $block_size )) $block_size.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: # With KEEP_SIZE; # Without KEEP_SIZE; fallocate: File too large. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
