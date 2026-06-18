# sources/test-tools/stress-ng/core-workload.c

## Purpose
`core-workload.c` implements small synthetic work kernels used to waste a controlled amount of time with different CPU, memory, syscall, vector, and formatting behaviors.

## Important APIs, Types, And Functions
`workload_methods` maps method names to `STRESS_WORKLOAD_METHOD_*` IDs, and `stress_workload_method` returns names by index. The public `stress_workload_waste_time` runs one selected workload or randomized workloads until a time deadline. Internal methods include FMA arithmetic, NOP loops, architecture pause/yield instructions, process-name mutation, cache-flushing memory reads, string/number conversion, square-root/hypot math, integer vector math, and floating-point vector math.

## Control Flow
The dispatcher computes `t_end = stress_time_now() + run_duration_sec`, chooses a method (`all` chooses a random nonzero method once, while `random` chooses repeatedly), and loops until the deadline. Workloads consume buffers supplied by the caller for memory and formatting methods. Vector and FMA helpers are annotated with `TARGET_CLONES` when enabled so the compiler can dispatch optimized variants.

## State And Persistence
State is minimal but includes static counters in vector helpers and a static volatile `val` for increment workload. The process name workload persistently changes the running process name during execution. No files are written.

## Dependencies And Integration Points
It depends on architecture assembly helpers, CPU cache flushing, random number generation, safe memory/string shims, `core-target-clones.h`, `core-vecmath.h`, math library functions, and `stress_time_now`. The workload stressor and any scheduler/load simulation code can use the methods table for option parsing.

## Risks
`STRESS_WORKLOAD_METHOD_MAX` is currently defined as `STRESS_WORKLOAD_METHOD_VECFP`, excluding `VECINT` from random/all selection even though `VECINT` exists; this may be intentional or a coverage gap. Buffer length assumptions matter for `memmove(buffer, buffer + 1, buffer_len - 1)` and vector reads. Repeated `stress_time_now` calls use wall-clock time, so clock adjustments can affect run duration.

## Test Signals
The `workload` stressor and `kernel-coverage.sh` cases for workload schedulers, distributions, and thread counts exercise this file. Build coverage with and without vector math and target clones validates fallback paths.
