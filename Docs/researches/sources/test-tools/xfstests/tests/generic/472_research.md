# sources/test-tools/xfstests/tests/generic/472

## Purpose
Test various swapfile activation oddities. It is registered as generic/472 with `_begin_fstest` tags `auto, quick, swap`, making it part of the swapfile activation coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, swapfile_cycle. Important state variables and paths include swapfile=$SCRATCH_MNT/swap, len=$((2 * 1048576)). Topic focus: swapfile activation. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; writes deterministic byte patterns.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, swapfile_cycle.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_swapfile; _require_test_program mkswap; _require_test_program swapon.

External/helper commands: $ATTR_PROG, $CHATTR_PROG, rm, swapoff, swapon, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: regular swap; too long swap; tiny swap. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
