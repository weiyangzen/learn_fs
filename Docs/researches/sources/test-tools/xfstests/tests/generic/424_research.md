# sources/test-tools/xfstests/tests/generic/424

## Purpose
Test the statx stx_attribute flags that can be set with chattr. It is registered as generic/424 with `_begin_fstest` tags `auto, quick`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testfile=$TEST_DIR/$seq-file, a_supported=, c_supported=, d_supported=, i_supported=, a_list=0, c_list=0, d_list=0, i_list=0. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program stat_test; _require_statx; _require_command "$CHATTR_PROG" chattr.

External/helper commands: $ATTR_PROG, $CHATTR_PROG, attr, rm, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
