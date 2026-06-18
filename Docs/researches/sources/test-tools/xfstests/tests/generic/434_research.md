# sources/test-tools/xfstests/tests/generic/434

## Purpose
Tests vfs_copy_file_range() error checking. It is registered as generic/434 with `_begin_fstest` tags `auto, quick, copy_range`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$TEST_DIR/test-$seq. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_xfs_io_command "copy_range"; _require_test; _require_mknod.

External/helper commands: $XFS_IO_PROG, md5sum, mkdir, mkfifo, mknod, rm.

Representative `xfs_io` operations: copy_range -s 1000 -l 100 $testdir/file; pwrite -S 0x61 0 1000; copy_range -s 0 -l 100 $testdir/file.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Create the original files; Try to copy when source pos > source size; d41d8cd98f00b204e9800998ecf8427e  TEST_DIR/test-434/copy; Try to copy to a read-only file; copy_range: Bad file descriptor; d41d8cd98f00b204e9800998ecf8427e  TEST_DIR/test-434/copy. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
