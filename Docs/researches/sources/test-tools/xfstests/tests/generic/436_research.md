# sources/test-tools/xfstests/tests/generic/436

## Purpose
More SEEK_DATA/SEEK_HOLE sanity tests. It is registered as generic/436 with `_begin_fstest` tags `auto, quick, rw, seek, prealloc`, making it part of the preallocation/range operations, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include tmp=$$, BASE_TEST_FILE=$TEST_DIR/seek_sanity_testfile. Topic focus: preallocation/range operations, holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_seek_data_hole; _require_xfs_io_command "falloc"; _require_test_program "seek_sanity_test".

External/helper commands: rm.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
