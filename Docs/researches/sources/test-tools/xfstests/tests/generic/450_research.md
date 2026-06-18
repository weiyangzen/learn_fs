# sources/test-tools/xfstests/tests/generic/450

## Purpose
Test read around EOF. If the file offset is at or past the end of file, no bytes are read, and read() returns zero. There was a bug, when DIO read offset is just past the EOF a little, but in the same block with EOF, read returns different negative values. The following two kernel commits fixed this bug: 74cedf9b6c60 direct-io: Fix negative return from dio read beyond eof 2d4594acbf6d fix the regression from "direct-io: Fix negative return from dio read beyond eof". It is registered as generic/450 with `_begin_fstest` tags `auto, quick, rw`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, check_xfs_io_read, read_test. Important state variables and paths include tfile=$TEST_DIR/testfile_${seq}, ssize=`$here/src/min_dio_alignment $TEST_DIR $TE..., bsize=`_get_block_size $TEST_DIR`, asize=$((bsize * 2)), tsize=$((asize - ssize * 2)). Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup, check_xfs_io_read, read_test.

## State and Persistence Behavior
uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_test; _require_odirect.

External/helper commands: $XFS_IO_PROG, rm.

Representative `xfs_io` operations: pread 0 $ssize; pread $bsize $bsize; pread $tsize $ssize; pread $((tsize + ssize)) $ssize; pread $((bsize * 100)) $ssize; pwrite 0 ${tsize}; fsync.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: buffer read the first sector within EOF; buffer read the second block contains EOF; buffer read a sector at (after) EOF; buffer read the last sector past EOF; buffer read at far away from EOF; direct read the first sector within EOF. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
