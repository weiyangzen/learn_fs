# File Research: sources/os/bsd/freebsd-src/sys/sys/bitcount.h

## Purpose
`bitcount.h` provides FreeBSD population-count helpers for 16-, 32-, 64-bit, `long`, and `int` values.

## Main Interfaces
- Constant-expression helpers: `__const_bitcount8`, `__const_bitcount16`, `__const_bitcount32`, and `__const_bitcount64`.
- Runtime helpers: `__bitcount16`, `__bitcount32`, `__bitcount64`, `__bitcountl`, and `__bitcount`.

## Implementation Notes
When `__POPCNT__` is available, the header maps to compiler builtins. Otherwise it uses SWAR-style arithmetic masks and shifts. On LP64, 64-bit counts are computed directly; on 32-bit platforms, 64-bit counts are split into two 32-bit halves.

## Dependencies and Constraints
Includes `sys/_types.h`. The names are internal-style double-underscore helpers, commonly used by higher-level bitset and bitstring code.
