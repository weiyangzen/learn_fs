# sources/storage-engines/wiredtiger/src/support/pow.c

## Purpose
`pow.c` contains small power-of-two and integer log helpers. It provides active helpers for integer log2, power-of-two testing, and rounding up to a power-of-two multiple, plus optional unused next-largest-power-of-two routines behind `__WIREDTIGER_UNUSED__`.

## Important APIs, Types, and Functions
The active functions are `__wt_log2_int(uint32_t n)`, `__wt_ispo2(uint32_t v)`, and `__wt_rduppo2(uint32_t n, uint32_t po2)`. Optional compiled-out helpers are `__wt_nlpo2_round` and `__wt_nlpo2`, both based on classic bit-hack propagation of the highest set bit.

## Control Flow
`__wt_log2_int` shifts right until the input becomes zero and counts shifts, returning floor log2 for positive inputs. `__wt_ispo2` returns true when `v & (v - 1)` is zero. `__wt_rduppo2` first verifies `po2` with `__wt_ispo2`, computes the shift count, rounds `n` up to the next multiple using shift arithmetic, and asserts no overflow; it returns zero if `po2` is not a power of two.

## State and Persistence Behavior
The functions are pure and maintain no state. They do not allocate, lock, or persist anything.

## Dependencies and Integration Points
The file includes `wt_internal.h` for types, assertions, and build macros. These helpers are used by internal sizing and alignment code that needs cheap integer math without floating point.

## Risks
`__wt_ispo2(0)` returns true by design of the bit expression, and the comment explicitly calls this out. Callers that require positive powers of two must check nonzero separately. `__wt_rduppo2` can produce surprising output for `n == 0` because unsigned arithmetic wraps through `n - 1`; callers should avoid zero unless that behavior is intended. Very large `n` can overflow the rounded result, caught by assertion but still a contract concern in release builds.

## Test Signals
Tests should cover log2 for 0, 1, powers of two, and adjacent values; `__wt_ispo2` for 0, powers, and non-powers; and `__wt_rduppo2` for common alignments, non-power `po2`, already aligned input, just-over-boundary input, zero input, and values near `UINT32_MAX`.
