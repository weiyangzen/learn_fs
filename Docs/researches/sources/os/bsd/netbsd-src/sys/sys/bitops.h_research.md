# File Research: sources/os/bsd/netbsd-src/sys/sys/bitops.h

## Scope

Provides inline bit operations, integer log helpers, fast 32-bit division helpers, and typed bitmap macros.

## APIs And Behavior

- Defines fallback `ffs32`, `ffs64`, `fls32`, and `fls64`.
- `ilog2()` uses compile-time expansion for constants and `fls32/fls64` for runtime values, returning `-1` for zero.
- `fast_divide32_prepare()` precomputes multiplier and shifts; `fast_divide32()` and `fast_remainder32()` use them to replace division by a fixed divisor.
- Bitmap helpers define typed bitmap structs and macros for size, word, bit, set, clear, test, and zero.

## Dependencies

- Includes `sys/stdint.h`; uses `NBBY`, `__GNUC_PREREQ__`, `__arraycount`, and compiler builtins from common headers.

## Risks And Invariants

- `fast_divide32_prepare()` expects a valid nonzero divisor.
- Bitmap macros rely on GNU `__typeof__`.
- `ilog2()` macro evaluates size/type paths differently for constants and variables.
