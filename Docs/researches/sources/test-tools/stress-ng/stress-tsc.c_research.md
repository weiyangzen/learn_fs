# sources/test-tools/stress-ng/stress-tsc.c

## Purpose
Implements the `tsc` stressor, a CPU counter-read workload that repeatedly reads the architecture's time stamp or timebase counter and optionally verifies monotonic increase.

## Important APIs, Types, And Functions
Architecture-specific `rdtsc()` implementations cover LoongArch `rdtime`, RISC-V `rdtime`, x86 `rdtsc`, PowerPC `__ppc_get_timebase`, s390 `stck`, and SPARC tick. `stress_tsc_supported()` checks runtime support: RISC-V probes SIGILL recovery, x86 checks CPU identity and TSC feature flags, and other supported architectures return success. x86 optionally defines `lfence()` and `rdtscp` paths. Macros `TSCx32`, `TSCx32_verify`, `TSCPx32`, and lfence variants unroll counter reads 32 times. `stress_tsc_check()` verifies monotonicity with wraparound tolerance. `stress_tsc_generic()`, `stress_tsc_lfence()`, and `stress_tsc_rdtscp()` drive the selected read loop.

## Control Flow
After synchronization, `stress_tsc()` resolves `tsc-lfence` and `tsc-rdtscp`. Unsupported or non-x86-specific options log informational messages and fall back; `rdtscp` disables lfence when both are requested. If `tsc_supported` is true, it chooses verification based on global verify flags and calls the selected loop. Each loop measures elapsed wall time around four blocks of 32 reads, increments bogo ops once per 128 reads, and optionally checks the last read of each block against the previous saved counter. On exit it reports nanoseconds per time counter read.

## State And Persistence Behavior
State is process-local: support flags, optional RISC-V signal jump buffer, stack-local counters, and accumulated duration. No persistent system state or files are used.

## Dependencies And Integration Points
The file integrates with stress-ng architecture assembly helpers, CPU feature detection, signal wrappers, settings, sync, proc-state, bogo accounting, and metrics. It registers a `supported` callback, `CLASS_CPU`, `VERIFY_OPTIONAL`, and options for x86 lfence and rdtscp. Unsupported architectures export `stress_unimplemented`.

## Risks And Test Signals
Counters may be unavailable, trap, be virtualized poorly, or appear non-monotonic across CPU migration on broken systems. Verification tolerates high-bit wraparound but otherwise fails on non-increasing values. Serialized lfence and rdtscp paths measure different costs than plain reads. Test signals include skip messages for unsupported CPUs or disallowed RISC-V rdtime, monotonicity failure logs, nanoseconds/read metric, and option fallback messages for unsupported x86-specific modes.
