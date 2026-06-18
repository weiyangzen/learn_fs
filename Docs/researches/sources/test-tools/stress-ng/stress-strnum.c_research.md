# sources/test-tools/stress-ng/stress-strnum.c

## Purpose
Implements the `strnum` stressor, which repeatedly converts randomized numeric values to and from strings using libc conversion APIs. It stresses integer, unsigned integer, floating-point, scanning, formatting, and C23-style `strfrom*` paths while verifying that each conversion stays within exact or tolerance-based expectations.

## Important APIs, Types, And Functions
`stress_strnum_method_t` names each conversion method and points to a `stress_strnum_func_t`. The global aligned value/string pairs hold the current randomized int, long, long long, unsigned variants, float, double, and long double data. `stress_strnum_set_values()` refreshes those values and their canonical string forms. Method functions wrap `atoi`, `atol`, `atoll`, conditional `strtoul`, `strtoull`, `strtof`, `strtod`, `strtold`, `strfromf`, `strfromd`, `strfroml`, multiple `sscanf` forms, and `snprintf` forms. `stress_strnum_call_method()` times 1000 calls per bogo operation and updates per-method metrics. `stress_strnum_all()` runs every method except itself.

## Control Flow
`stress_strnum()` resolves `strnum-method`, waits at the global start barrier, clears per-method metrics, initializes random values, then loops until the stress-ng stop condition. Each loop invokes the selected method, marks failure if verification fails, refreshes random values every 1000 outer iterations, and increments bogo operations inside the method caller. After stopping, it emits call-per-second metrics for methods that accumulated timing data and sets deinit state.

## State And Persistence
State is process-local and held in static globals: current numeric values, canonical strings, and the metrics array. No filesystem or kernel object persists. The only cross-iteration state is refreshed random data and accumulated per-method timing/count values.

## Dependencies And Integration Points
Depends on stress-ng option handling, bogo counters, timing, metrics, random number generation, failure logging, sync barriers, and shim math helpers. Compile-time feature macros gate optional libc functions so the method table matches the target C library. The exported `stress_strnum_info` uses `VERIFY_ALWAYS`, CPU/compute/hot classification, and a method option callback.

## Risks And Test Signals
Floating-point checks use fixed tolerances and truncated string formats, so platform formatting or long-double precision differences can affect pass/fail behavior. Global static state means each worker has private process state, but this would not be thread-safe if reused differently. `strfrom*` comparisons intentionally compare only a truncated prefix around the decimal point, reducing false failures but also reducing strictness. Test signals are no `pr_fail()` conversion mismatches, populated per-method metrics, and successful operation of the `all` method across the compile-time enabled method table.
