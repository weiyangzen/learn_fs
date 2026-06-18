# sources/test-tools/xfstests/tests/generic/465

## Purpose
Test i_size is updated properly under dio read/write. It is registered as generic/465 with `_begin_fstest` tags `auto, rw, quick, aio`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testfile=$TEST_DIR/$seq.$$, min_dio_align=`$here/src/min_dio_alignment $TEST_DIR $TE..., page_size=`$here/src/feature -s`, align=$min_dio_align. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_aiodio aio-dio-append-write-read-race; _require_test_program "feature".

External/helper commands: rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: non-aio dio test; aio-dio test. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
