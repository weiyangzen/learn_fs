# File Research: sources/os/bsd/netbsd-src/lib/libm/src/math_private.h

This private header defines the shared low-level infrastructure used throughout NetBSD libm.

It provides endian-aware unions and macros for extracting and setting float, double, ld80, and ld128 bit fields; strict-assignment helpers for excess precision; x86 precision-control macros; two-sum and three-sum normalization macros; NaN mixing helpers; complex construction helpers; prototypes for IEEE elementary functions and kernel functions; and utility rounding helpers `rnint`, `rnintf`, `rnintl`, `irint`, and `i64rint`.

It also defines fast floor macros for `sinpi`/`cospi`-style functions, `struct Double`, declarations for legacy high/low precision helpers, and prototypes for reduced float and long-double trig kernels. Correctness depends on matching machine IEEE layout headers, `BYTE_ORDER`, `union ieee_ext_u`, and C floating-evaluation behavior.
