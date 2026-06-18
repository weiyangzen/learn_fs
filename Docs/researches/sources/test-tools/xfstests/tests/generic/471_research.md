# sources/test-tools/xfstests/tests/generic/471

## Purpose
Test that if names are added to a directory after an opendir(3) call and before a rewinddir(3) call, future readdir(3) calls will return the names. This is mandated by POSIX: https://pubs.opengroup.org/onlinepubs/007904875/functions/rewinddir.html. It is registered as generic/471 with `_begin_fstest` tags `auto, quick, dir`, making it part of the filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include target_dir=$TEST_DIR/test-$seq. Topic focus: filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_test; _require_test_program rewinddir-test.

Documented regression fixes: _fixed_by_fs_commit btrfs e60aa5da14d0 "btrfs: refresh dir last index during a rewinddir(3) call".

External/helper commands: mkdir, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
