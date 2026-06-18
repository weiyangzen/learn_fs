# sources/test-tools/stress-ng/stress-monte-carlo.c

Purpose: implements `monte-carlo`, a CPU/compute stressor that estimates mathematical constants and integrals using configurable random number generators and sample counts.

Important APIs/types/functions: `stress_monte_carlo_rand_info_t` maps RNG names to `rand`, `seed`, and `supported` functions. RNGs include MWC32/MWC64, LCG, PCG32, xorshift, and optional arc4random, getrandom, drand48, random, PPC DARN, and x86 RDRAND. `stress_monte_carlo_method_t` maps methods for `pi`, `e`, `exp`, `sin`, `sqrt`, and `squircle` to expected values. `stress_monte_carlo_by_method()` and `stress_monte_carlo_by_rand()` expand `all` selections and accumulate metrics/results.

Control flow: the stressor detects supported RNGs, initializes metrics/result matrices, reads options `monte-carlo-method`, `monte-carlo-rand`, and `monte-carlo-samples`, synchronizes, then repeatedly runs selected method/RNG combinations. Each method processes samples in bounded 16K chunks and exits early on global stop. On deinit it emits samples/sec metrics per method/RNG and debug comparisons of averages versus expected values.

State and persistence: RNG state is static for LCG, PCG32, xorshift, getrandom buffer index, and stress-ng MWC seeds. Metrics and result accumulators are stack-local. No external state is changed.

Dependencies and integration: uses libm wrappers, architecture RNG helpers, `getrandom`, option method enumeration, stress-ng metrics, bogo counters, and process synchronization.

Risks and test signals: estimates are stochastic and not verification failures; small sample counts can be inaccurate. RNG support varies by architecture and libc. Test signals are method/RNG option enumeration, nonzero samples/sec metrics, debug result summaries, and no divide-by-zero when stop occurs after partial sample processing.
