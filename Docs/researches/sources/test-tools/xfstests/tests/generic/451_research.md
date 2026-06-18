# sources/test-tools/xfstests/tests/generic/451

## Purpose
Test data integrity when mixing buffered reads and asynchronous direct writes a file. It is registered as generic/451 with `_begin_fstest` tags `auto, quick, rw, aio`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include TESTFILE=$TEST_DIR/tst-aio-dio-cycle-write.$seq, FSIZE=655360, nr_cpu=`$here/src/feature -o`, loops=$((nr_cpu / 2)), keep_reading=$tmp.reading. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_test; _require_test_program "feature"; _require_aiodio aio-dio-cycle-write; _require_command "$TIMEOUT_PROG" timeout.

External/helper commands: $XFS_IO_PROG, rm, touch.

Representative `xfs_io` operations: pread 0 $FSIZE.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
