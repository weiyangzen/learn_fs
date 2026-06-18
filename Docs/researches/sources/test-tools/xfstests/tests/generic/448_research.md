# sources/test-tools/xfstests/tests/generic/448

## Purpose
Check what happens when SEEK_HOLE/SEEK_DATA are fed negative offsets. It is registered as generic/448 with `_begin_fstest` tags `auto, quick, rw, seek`, making it part of the holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include BASE_TEST_FILE=$TEST_DIR/seek_sanity_testfile_$seq. Topic focus: holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_seek_data_hole; _require_test_program "seek_sanity_test".

External/helper commands: rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
