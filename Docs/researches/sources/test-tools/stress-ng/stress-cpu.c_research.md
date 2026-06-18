# sources/test-tools/stress-ng/stress-cpu.c

## Purpose
This is stress-ng's general CPU compute workload. It exposes many selectable CPU methods covering integer arithmetic, floating point, complex math, checksums, recursion, branch behavior, conversions, division, image-style dithering, matrix multiplication, primality, statistics, and mathematical constants. The default `all` method rotates across the method table to provide broad CPU coverage.

## Important APIs, Types, And Functions
`stress_cpu_method_info_t` maps method names to `stress_cpu_func` callbacks and normalization rates. The method table includes hand-written kernels such as `stress_cpu_sqrt()`, `stress_cpu_gcd()`, `stress_cpu_fft()`, `stress_cpu_matrix_prod()`, `stress_cpu_prime()`, `stress_cpu_stats()`, and many generated kernels produced by `STRESS_CPU_INT`, `STRESS_CPU_FP`, `STRESS_CPU_COMPLEX`, and `STRESS_CPU_INT_FP`. `stress_call_cpu_method()` dispatches one method and updates normalized bogo count. `stress_per_cpu_time()` selects process CPU time when available. `stress_cpu()` implements option handling, load throttling, dispatch, and cleanup.

## Control Flow
At startup `stress_cpu()` catches `SIGILL`, reads `cpu-load`, `cpu-load-slice`, `cpu-method`, and `cpu-old-metrics`, initializes per-method scale factors, waits at the sync barrier, and either sleeps for zero-load, spins at 100% load, or enters a throttled load loop. In full-load mode it disables FP subnormal handling, calls the selected method until stop or failure, then restores subnormal handling. In partial-load mode it runs a slice by fixed iteration count, random CPU-time window, or requested millisecond duration, computes the sleep delay needed to approximate the requested CPU percentage, sleeps with `select()` or nanosleep, and carries timing bias forward.

## State And Persistence
Most methods are stateless across calls except deliberate static buffers and accumulators, such as FFT buffers, matrix arrays, dither pixels, parity table, logistic map state, and LFSR state. Stress-ng global flags control verification and load settings. Metrics are bogo counts normalized by per-method rates unless `cpu-old-metrics` is requested. There is no external persistent state.

## Dependencies And Integration Points
This file depends heavily on stress-ng core math shims, random generators, bitops, network checksum helper, put helpers that prevent optimization, target-clone attributes, architecture feature macros, and the option parser. Compile-time feature checks include complex arithmetic, decimal and extended floating types, 128-bit integers, compiler builtins, and architecture exclusions such as S390 decimal math.

## Risks
Many verification checks rely on exact or tolerance-based numeric results that can vary with compiler, libc, architecture, floating mode, and optimization flags. Some generated mixed int/fp methods intentionally rely on overflow semantics for unsigned types; accidental signed conversions would be risky. The `all` dispatcher uses a static method index, so behavior is process-local and rotating. Load throttling is approximate and can be distorted by CPU affinity, scheduler noise, and wall-clock/CPU-clock mismatches.

## Test Signals
Key signals are successful method selection for every advertised `cpu-method`, verify-mode pass across supported architectures, stable partial-load behavior, no `SIGILL` from unsupported generated instructions, and sane normalized bogo counts. Targeted tests should exercise optional complex, decimal, float128, int128, and rand48 paths on platforms that expose them.
