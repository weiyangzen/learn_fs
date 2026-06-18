# sources/test-tools/xfstests/tests/generic/428

## Purpose
This is a regression test for kernel patch: dax: fix data corruption due to stale mmap reads created by Ross Zwisler <ross.zwisler@linux.intel.com>. It is registered as generic/428 with `_begin_fstest` tags `auto, quick, dax, mmap`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "t_mmap_stale_pmd".

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
