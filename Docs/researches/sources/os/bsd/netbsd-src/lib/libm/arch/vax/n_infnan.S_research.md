# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_infnan.S

## Scope

Provides the old VAX `infnan(int)` helper used by other assembly math routines to set `errno` and generate a reserved-operand fault.

## APIs And Behavior

- Accepts `EDOM`, `ERANGE`, or `-ERANGE`-style intent, though the implementation distinguishes only `ERANGE` from other values.
- Sets global `errno` to `ERANGE` for positive range overflow, otherwise `EDOM`.
- Executes an `emodd` operation with reserved-operand pattern `0x8000` to trigger the VAX reserved operand fault and returns if execution continues.

## Dependencies And Risks

- Used by VAX `sqrt`, `scalb`, `scalbn`, and related error paths.
- Assumes `_C_LABEL(errno)` is writable from libm assembly.
- Non-IEEE behavior is intentionally fault-oriented rather than returning IEEE NaN/Inf values.
