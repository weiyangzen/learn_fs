# sources/test-tools/stress-ng/stress-ctrig.c

## Purpose
This stressor exercises C complex trigonometric functions for `cos`, `sin`, and `tan` across float, double, and long-double variants when the platform exposes them. It accumulates deterministic sums over a fixed complex path and verifies the results against precomputed tolerances.

## Important APIs, Types, And Functions
`stress_ctrig_method_t` maps method names to boolean test callbacks. Methods include `stress_ctrig_ccos()`, `stress_ctrig_ccosf()`, `stress_ctrig_ccosl()`, `stress_ctrig_csin*()`, and `stress_ctrig_ctan*()` variants behind feature macros. `stress_ctrig_exercise()` times a method, updates metrics, and logs checksum failures. `stress_ctrig_all()` runs every concrete method. `stress_ctrig()` handles option selection, loop control, metrics, and process state.

## Control Flow
Each concrete method initializes a complex value at roughly `-0.5 + 0.5i`, steps it by a small complex delta for `STRESS_CTRIG_LOOPS`, accumulates the shim complex trig result, increments bogo count, and returns true if the accumulated checksum exceeds the method-specific tolerance. The top-level stressor reads `ctrig-method`, zeroes metrics, synchronizes, repeatedly calls the selected method, and fails the stressor on the first checksum mismatch.

## State And Persistence
State is limited to static expected sums, the method table, and per-method metrics. There is no external persistence. The `all` method uses nested metrics updates for concrete methods and reports rates for methods with observed durations.

## Dependencies And Integration Points
This file depends on `complex.h`, stress-ng complex shims, math library functions, target-clone and pragma helpers, and option parsing through `OPT_ctrig_method`. Without complex support it registers as unimplemented while preserving option metadata.

## Risks
Complex math results vary with libc accuracy, long-double representation, compiler optimization, and architecture, so tolerances are intentionally different for float/double/long-double. The methods are verify-always, making platform math regressions visible as stressor failures. Missing feature macros shrink the method table, so option indexes must come from the generated selector.

## Test Signals
Signals include all advertised methods passing checksum verification, per-method operations-per-second metrics, correct unimplemented behavior without `complex.h`, and stable tolerances on targets with 80-bit, 128-bit, or ordinary long-double formats.
