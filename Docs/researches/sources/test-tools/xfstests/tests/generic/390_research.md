# sources/test-tools/xfstests/tests/generic/390

## Purpose
Multi-threads freeze/unfreeze testing. This's a stress test case, it won't do functional check. It is registered as generic/390 with `_begin_fstest` tags `auto, freeze, stress`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include num_cpus=`$here/src/feature -o`, procs=$num_cpus, nops=1000, stress_dir=$SCRATCH_MNT/fsstress_test_dir, fsstress_args=`_scale_fsstress_args -d $stress_dir -p $p..., result=$?. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_freeze; _require_test_program "feature".

External/helper commands: mkdir, rm.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
