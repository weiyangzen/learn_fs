# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/softfloat.h

This header declares the m68k SoftFloat public API and type layout. It enables `FLOATX80` except on ColdFire, leaves `FLOAT128` disabled, defines `float32`, `float64`, and a packed m68k `floatx80` layout with `X80SHIFT` and `X80M68K`.

It exposes global rounding, tininess, exception-flag, exception-mask, and extended-precision state, mapped to NetBSD `<machine/ieeefp.h>` constants. It declares integer conversion, float32/float64 arithmetic, comparisons, NaN predicates, floatx80 conversions/operations/comparisons, and conditional float128 operations.

This file is consumed by the architecture softfloat implementation and GCC compatibility paths. The most sensitive details are the m68k extended-precision memory layout and conditional declarations under `SOFTFLOAT_FOR_GCC` / `SOFTFLOATM68K_FOR_GCC`.
