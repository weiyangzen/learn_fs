# sources/test-tools/stress-ng/stress-goto.c

## Purpose
`stress-goto.c` implements the `goto` CPU stressor, a branch-prediction and instruction-flow workload built around GCC-style labels-as-values. It starts workers that repeatedly jump through 1024 generated labels in forward, backward, or random direction and reports "million gotos per sec".

## Important APIs, Types, And Functions
The user-facing options are `goto-direction` and `goto-ops`; `stress_goto_direction()` maps method indices to `forward`, `backward`, and `random`. `MAX_LABELS` is 0x400. The `G(n)` macro emits each label body, increments every 64th label counter, and jumps through the active label table. `stress_goto()` builds `labels_forward` and `labels_backward` from the static `default_labels` table, selects the requested direction, drives the loop with `stress_continue()`, and records metrics. `stress_goto_info` registers the stressor as `CLASS_CPU` with `VERIFY_ALWAYS`.

## Control Flow
On supported compilers, startup initializes forward/backward transition arrays, reads the selected direction, waits at the stress-ng sync barrier, then enters label `L0x000`. Each full 1024-label pass increments the bogo counter. In random mode the active label array is switched between forward and backward using `stress_mwc1()` before each pass. On termination it checks sampled label counters against the bogo counter and computes gotos/second.

## State And Persistence
State is process-local: static label arrays, a static counter array, the global stress-ng bogo counter, and a metrics record. It writes no files and has no persistent external state.

## Dependencies And Integration Points
The implementation depends on `HAVE_LABEL_AS_VALUE`, compiler feature gates, stress-ng random/time/sync/metrics helpers, and compiler-specific optimization controls. It is unimplemented on PCC or compilers without labels-as-values.

## Risks
The generated label table is large and brittle: missing or misordered labels break the branch walk. Compiler optimization can be expensive, so clang/icx are forced to `OPTIMIZE0`. Verification only samples every 64th label, so small unsampled errors could escape. This stressor is non-portable C by design.

## Test Signals
Useful signals are successful build on GNU-label compilers, correct unimplemented fallback on unsupported compilers, valid parsing of all `goto-direction` methods, no counter mismatches in verify mode, and plausible "million gotos per sec" metrics.
