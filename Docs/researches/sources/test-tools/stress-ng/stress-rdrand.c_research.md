# sources/test-tools/stress-ng/stress-rdrand.c research

Purpose: implements `rdrand`, a CPU stressor for hardware random-number instructions: x86 `rdrand`/optional `rdseed` and PPC64 `darn`.

Important APIs, types, and functions: architecture blocks define `rand64()` and optional `seed64()` wrappers using stress-ng assembly helpers. `stress_rdrand_supported()` validates CPU feature availability and sets `rdrand_supported`. `RAND64x32` and `SEED64x32` unroll instruction calls. `stress_rdrand_sane()` checks that repeated random reads change and reports unlikely repeats.

Control flow: `stress_rdrand()` resolves `rdrand-seed`, falls back if `rdseed` is unavailable, synchronizes, performs sanity checks, then loops over batches of heavily unrolled random reads. It samples nibbles from selected bit positions into 16 counters and advances bogo by batch count. After termination it emits million-random-bits metrics and checks whether bucket counts deviate more than 5 percent when enough samples exist.

State and persistence: only static per-process counters and support flag are used. There is no persistent state.

Dependencies and integration: depends on architecture detection, CPU feature helpers, assembly instruction wrappers, optional builtin CPU checks on PPC64, and stress-ng metrics/options. It registers supported callback, CPU class, and `VERIFY_ALWAYS`.

Risks: hardware RNG instructions can be unavailable, emulated poorly, or transiently fail in ways hidden by helper semantics. The distribution check is simple and may produce false failures on short or biased samples. `rdseed` is slower and may be less available.

Test signals: unsupported CPU skip, sanity failure for unchanged values, duplicate informational messages, million bits/read rate metrics, and poor-distribution failure logs.
