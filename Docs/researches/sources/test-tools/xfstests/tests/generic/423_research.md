# sources/test-tools/xfstests/tests/generic/423

## Purpose
Test the statx system call. It is registered as generic/423 with `_begin_fstest` tags `auto, quick`, making it part of the preallocation/range operations, rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include target=$TEST_DIR/$seq-nowhere. Topic focus: preallocation/range operations, rename/link persistence, filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "stat_test"; _require_test_program "af_unix"; _require_statx; _require_symlinks; _require_mknod.

External/helper commands: dd, ln, mkdir, mkfifo, mknod, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Test statx on a fifo; Test statx on a chardev; Test statx on a directory; Test statx on a blockdev; Test statx on a file; 20+0 records in. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
