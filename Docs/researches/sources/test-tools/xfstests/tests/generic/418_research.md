# sources/test-tools/xfstests/tests/generic/418

## Purpose
Test pagecache invalidation in buffer/direct write/read combination. Fork N children, each child writes to and reads from its own region of the same test file, and check if what it reads is what it writes. The test region is determined by N * blksz. Write and read operation can be either direct or buffered. Regression test for commit c771c14baa33 ("iomap: invalidate page caches should be after iomap_dio_complete() in direct write"). It is registered as generic/418 with `_begin_fstest` tags `auto, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: runtest. Important state variables and paths include diotest=$here/src/dio-invalidate-cache, testfile=$TEST_DIR/$seq-diotest, sectorsize=`$here/src/min_dio_alignment $TEST_DIR $TE..., pagesize=`$here/src/feature -s`, t_cases=(. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions runtest.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_odirect; _require_block_device $TEST_DEV; _require_test_program "dio-invalidate-cache"; _require_test_program "feature".

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
