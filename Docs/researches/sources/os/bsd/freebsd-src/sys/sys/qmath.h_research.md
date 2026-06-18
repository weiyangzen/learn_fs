# File Research: sources/os/bsd/freebsd-src/sys/sys/qmath.h

Read completely: 638 lines.

## Purpose
Provides macro-based fixed-point “Q” number types and arithmetic/conversion helpers with embedded control bits describing fractional precision.

## Main Elements
- Defines signed/unsigned Q storage typedefs from 8-bit through 64-bit and max aliases.
- Reserves the low 3 bits of each value for precision control, encoding fractional precision as 2, 4, 6, 8, 16, 32, 48, or 64 effective bits subject to storage size.
- Defines macros for type casting, total/control/fractional/integer/sign bit counts, radix shift, sign setting, control masks, integer/fraction masks, and raw/value getters/setters.
- Provides decimal-to-binary fractional conversion, initialization, C-string rendering, max string length calculation, float/double conversion, and debug printf format/data generation.
- Provides comparison and representability checks across Q values and integers.
- Provides value cloning/copying, addition/subtraction, multiplication/division, and fraction creation for Q-to-Q and Q-to-integer operations.
- Returns conventional errors such as `EINVAL`, `EOVERFLOW`, and `ERANGE` from arithmetic macros on invalid input, overflow, or underflow.

## Dependencies And Integration
Depends on integer types, compiler `__typeof`, bit scanning/popcount builtins, and errno values provided by consumers. Intended for low-level fixed-point math without runtime helper functions.

## Risk Notes
This header is macro-heavy and evaluates some arguments multiple times. Precision normalization is explicitly incomplete (`Q_NORMPREC` returns `ERANGE` when precision differs), so callers must understand precision compatibility and side effects.
