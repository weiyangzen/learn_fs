# sources/test-tools/xfstests/tests/generic/433

## Purpose
Tests vfs_copy_file_range(): - Copy a small file - Use copy to swap data at beginning and end - Use copy to swap data in the middle - Use copy to swap data in a small file. It is registered as generic/433 with `_begin_fstest` tags `auto, quick, copy_range`, making it part of the swapfile activation coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$TEST_DIR/test-$seq. Topic focus: swapfile activation. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_xfs_io_command "copy_range"; _require_test.

External/helper commands: $XFS_IO_PROG, cmp, md5sum, mkdir, rm.

Representative `xfs_io` operations: copy_range $testdir/file; copy_range -s 0 -d 4 -l 1 $testdir/file; copy_range -s 4 -d 0 -l 1 $testdir/file; copy_range -s 1 -d 3 -l 1 $testdir/file; copy_range -s 3 -d 1 -l 1 $testdir/file; copy_range -s 1 -d 3 -l 4 $testdir/file.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Create the original file and then copy; Original md5sums:; ab56b4d92b40713acc5af89985d4b786  TEST_DIR/test-433/file; ab56b4d92b40713acc5af89985d4b786  TEST_DIR/test-433/copy; Swap beginning and end of original file; md5sums after swapping beginning and end:. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
