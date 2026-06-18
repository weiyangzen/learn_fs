# sources/test-tools/xfstests/tests/generic/463

## Purpose
Test racy COW AIO write completions. It is registered as generic/463 with `_begin_fstest` tags `auto, quick, clone`, making it part of the reflink/shared extents coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: reflink/shared extents. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; exercises clone/dedupe shared-extent operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_test; _require_test_reflink; _require_aiodio aio-dio-cow-race.

External/helper commands: rm.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
