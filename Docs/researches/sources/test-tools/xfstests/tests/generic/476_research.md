# sources/test-tools/xfstests/tests/generic/476

## Purpose
Run an all-writes fsstress run with multiple threads to shake out bugs in the write path. It is registered as generic/476 with `_begin_fstest` tags `auto, rw, long_rw, stress, soak, smoketest`, making it part of the fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include nr_cpus=$((LOAD_FACTOR * 4)), nr_ops=$((25000 * TIME_FACTOR)), fsstress_args=(-w -d $SCRATCH_MNT -n $nr_ops -p $nr_cpus). Topic focus: fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_scratch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
