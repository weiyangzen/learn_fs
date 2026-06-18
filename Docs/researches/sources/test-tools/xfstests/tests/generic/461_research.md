# sources/test-tools/xfstests/tests/generic/461

## Purpose
Shutdown stress test - exercise shutdown codepath with fsstress, make sure we don't BUG/WARN. Coverage for all fs with shutdown. It is registered as generic/461 with `_begin_fstest` tags `auto, shutdown, stress`, making it part of the fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include SLEEP_TIME=$((10 * $TIME_FACTOR)), PROCS=$((4 * LOAD_FACTOR)), load_dir=$SCRATCH_MNT/test. Topic focus: fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; forces durability boundaries with sync/fsync operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_scratch_shutdown.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
