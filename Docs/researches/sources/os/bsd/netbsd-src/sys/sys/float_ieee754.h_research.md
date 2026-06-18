# File Research: sources/os/bsd/netbsd-src/sys/sys/float_ieee754.h

Read completely: 159 lines.

## Purpose
Supplies IEEE-754 `float.h` constants for machine-dependent `float.h` headers.

## Main Interfaces
- `_FLOAT_IEEE754`.
- `FLT_ROUNDS` via `__flt_rounds()`.
- Conditional `FLT_EVAL_METHOD`.
- GCC builtin-backed constants for `FLT_*` and `DBL_*`, with fallback literal definitions.
- Default `LDBL_*` definitions matching double precision when the machine header has not supplied extended precision.
- `DECIMAL_DIG` when visible by standards/profile macros.

## Dependencies And Integration
Includes cdefs and feature-test macros; intended to be included by a port's `float.h`, not used standalone.

## Risks And Edge Cases
- Long double defaults to double unless machine-specific header defines otherwise.
- Standards visibility controls `FLT_EVAL_METHOD` and `DECIMAL_DIG`.
- Older compiler fallback constants must match IEEE-754 assumptions.

## Filesystem Relevance
Low. General ABI/math support; no direct filesystem logic.
