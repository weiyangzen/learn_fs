# sources/test-tools/stress-ng/core-builtin.h

Purpose: broad portability shim that maps memory, complex math, scalar math, special functions, and rotate operations to compiler builtins, libc functions, intrinsics, or fallback expressions.

Important APIs and control flow: defines `shim_mem*`, `shim_strdup`, complex constructors, wrappers for pow/log/exp/trig/hyperbolic/Bessel/round/fabs/sqrt/fma families across float/double/long double and complex variants, plus rotate-left/right helpers for 8/16/32/64/128-bit values.

State and persistence: stateless macro/inline layer.

Dependencies and integration: included by core and stressor files to smooth compiler/libc differences; optionally includes `<x86intrin.h>`.

Risks and test signals: fallback math can have different precision/domain behavior from libc builtins; rotate helpers assume nonzero valid bit counts; macro wrappers can evaluate arguments in normal function-call form but still hide type conversions. Signals are successful builds against libcs missing long-double/complex functions and math stressor verification.
