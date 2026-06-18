# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/dtoa.c

Purpose: Implements David Gay's classic `dtoa()` conversion from native `double` to a decimal digit string.

Core behavior:
- Handles sign, zero, infinity, and NaN before numeric conversion.
- Supports modes 0-9 for shortest, ecvt-style, fcvt-style, and debug variants.
- Estimates decimal exponent `k = floor(log10(d))`, then corrects it when needed.
- Uses a fast floating-point path for small requested digit counts when correctness can be guaranteed.
- Falls back to multiprecision `Bigint` arithmetic for exact stopping and rounding decisions.
- Honors IEEE round-to-nearest/even and optional `Honor_FLT_ROUNDS` directed rounding.
- Returns allocated strings via `rv_alloc`/`nrv_alloc`; callers release with `freedtoa`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `d2b`, `i2b`, `pow5mult`, `lshift`, `multadd`, `quorem`, `cmp`, `diff`, `Balloc`, and `Bfree`.
- Depends on native double layout macros such as `word0`, `word1`, exponent masks, and endian definitions.
