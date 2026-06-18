# sources/test-tools/xfstests/tests/generic/430

## Purpose
Tests vfs_copy_file_range(): - Copy a file - Copy beginning of original to new file - Copy middle of original to a new file - Copy end of original to new file - Copy middle of original to a new file, creating a hole. It is registered as generic/430 with `_begin_fstest` tags `auto, quick, copy_range`, making it part of the holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$TEST_DIR/test-$seq. Topic focus: holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_xfs_io_command "copy_range"; _require_test.

External/helper commands: $XFS_IO_PROG, cmp, md5sum, mkdir, rm.

Representative `xfs_io` operations: copy_range $testdir/file; pwrite -S 0x61 0    1000; pwrite -S 0x62 1000 1000; pwrite -S 0x63 2000 1000; pwrite -S 0x64 3000 1000; pwrite -S 0x65 4000 1000; copy_range -l 1000 $testdir/file; copy_range -s 1000 -l 3000 $testdir/file; copy_range -s 4000 -l 1000 $testdir/file; copy_range -s 4000 -l 2000 $testdir/file.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Create the original file and then copy; Original md5sums:; e11fbace556cba26bf0076e74cab90a3  TEST_DIR/test-430/file; e11fbace556cba26bf0076e74cab90a3  TEST_DIR/test-430/copy; Copy beginning of original file; md5sums after copying beginning:. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
