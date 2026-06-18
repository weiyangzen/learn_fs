# File Research: sources/os/bsd/netbsd-src/lib/libc/time/difftime.c

## Purpose
Computes `double` difference between two `time_t` values while avoiding overflow where possible.

## Key Elements
Uses direct double subtraction when safe, unsigned arithmetic when `time_t` is unsigned, `uintmax_t` when wide enough, same-sign subtraction for signed values, and long double fallback for opposite-sign wide cases.

## Dependencies
Uses `private.h` for `time_t` and `TYPE_SIGNED`.

## Behavior/Risks
Carefully avoids signed overflow in most cases. The final wide opposite-sign fallback can suffer double rounding, as documented in the source.
