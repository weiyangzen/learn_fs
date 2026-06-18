# sources/test-tools/xfstests/tests/generic/477

## Purpose
Check open by file handle after cycle mount. This test uses load and store of file handles from a temp file to test decoding file handles after cycle mount and after directory renames. It is registered as generic/477 with `_begin_fstest` tags `auto, quick, exportfs`, making it part of the rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: create_test_files, test_file_handles. Important state variables and paths include NUMFILES=10, testroot=$TEST_DIR/$seq-dir, testdir=$testroot/testdir. Topic focus: rename/link persistence, filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions create_test_files, test_file_handles.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "open_by_handle"; _require_exportfs.

External/helper commands: mkdir, mount, mv, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: test_file_handles after cycle mount; test_file_handles after rename parent; test_file_handles after rename grandparent; test_file_handles after move to new parent. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
