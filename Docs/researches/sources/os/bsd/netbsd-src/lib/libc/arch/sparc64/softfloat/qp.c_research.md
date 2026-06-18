# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/qp.c

## Summary
Implements SPARC64 `_Qp*` quad-precision helper entry points on top of SoftFloat `float128`.

## Key Details
- Provides arithmetic helpers such as `_Qp_add`, `_Qp_sub`, `_Qp_mul`, `_Qp_div`, and `_Qp_sqrt`.
- Provides comparison helpers returning SPARC quad ABI comparison values or Boolean results.
- Converts between quad and `float`, `double`, signed integers, unsigned integers, `long`, and `unsigned long`.
- Uses `memcpy` to move bit representations between C floating types and SoftFloat integer storage.
- Implements `_Qp_neg` as subtraction from a static zero value.
- Handles unsigned 64-bit to quad conversion manually when the high bit is set.

## Notes
The file bridges compiler/runtime quad-precision ABI symbols to the software `float128` implementation.
