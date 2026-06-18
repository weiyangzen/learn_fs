# sources/test-tools/stress-ng/stress-intmath.c

## Purpose
`stress-intmath.c` stresses signed integer arithmetic across multiple widths by generating add, subtract, multiply, divide, and modulo kernels for standard and optional `int_fast*_t` types. It reports per-method million-operations-per-second metrics and verifies repeatability.

## Important APIs, Types, And Functions
`stress_intmath_vals_t` holds initial values and per-operation result slots for 128-bit, fast, 64/32/16/8-bit types as available. Macros `STRESS_INTMATH_ADD`, `SUB`, `MUL`, `DIV`, and `MOD` generate optimized kernels. `stress_intmath_method_t` maps method names to operation counts and generated callbacks. `stress_intmath_methods[]` covers standard widths; `stress_intfastmath_methods[]` covers fast widths when available. `stress_intmath_exercise()` primes a result slot, runs the selected method, updates metrics, and logs verification failures.

## Control Flow
`stress_intmath()` reads `intmath-method` and `intmath-fast`, rejects fast mode if unavailable, selects the method table, seeds four initial random values, clears initialized flags and metrics, waits at the barrier, then loops. Method `all` walks every concrete method each pass; otherwise only the selected method runs. After stop, it emits one metric per method with nonzero duration.

## State And Persistence
State is stack-local arithmetic values plus static metrics and initialization flags. It has no external persistent state.

## Dependencies And Integration Points
It depends on compile-time integer type detection, optional `__int128_t`, stress-ng random helpers, option parsing, metrics, target-clone/pragmas, and global verify flags.

## Risks
The file intentionally exercises signed overflow-prone expressions; behavior can be compiler- and optimization-sensitive even though verification compares repeatability within the same run. Fast-integer method indices depend on availability. `opts` bounds for `intmath-method` are minimal because the callback enumerates methods dynamically. Metrics assume hard-coded operation counts per generated kernel.

## Test Signals
Signals include verify-mode repeatability across all generated methods, fast-mode skip or success by platform, no divide-by-zero, plausible per-method M-ops metrics, and successful builds with/without int128 and int_fast types.
