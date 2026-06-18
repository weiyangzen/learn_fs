# sources/test-tools/stress-ng/stress-rotate.c

Purpose: implements `rotate`, a CPU/integer stressor for rotate-left and rotate-right operations over 8, 16, 32, 64, and optionally 128-bit integer widths.

Important APIs/types/functions: `stress_rotate_func_t` is the per-method function type. Macro families `STRESS_ROTATE_HELPER` and `STRESS_ROTATE` generate helpers and verified wrappers around `shim_rol*()` and `shim_ror*()`. `stress_rotate_funcs[]` maps method names including `all`, `rol8`, `ror8`, through optional 128-bit methods. `stress_rotate_info` exposes `rotate-method`.

Control flow: `stress_rotate()` zeroes metrics, resolves the method, checks global verify mode, synchronizes, and repeatedly calls the selected method. Method `all` dispatches every concrete method. Each helper seeds four random values, runs `ROTATE_LOOPS` rounds on all four, stores checksums through `stress_put_*()` to prevent optimization, and returns elapsed time. Verification reruns with restored RNG seed and compares checksums.

State and persistence: state is process-local metric accumulators and RNG seed snapshots. No external state is created.

Dependencies and integration points: depends on `core-builtin` rotate shims, `core-put` anti-optimization sinks, stress-ng method option parsing, metrics, random number generation, and optional `__uint128_t` support.

Risks and test signals: compiler optimization can otherwise fold rotate loops, so checksum sinks are important. Verification catches inconsistent helper output. Metrics report rotate operations per second per concrete method; failure is a checksum mismatch or invalid method resolution.
