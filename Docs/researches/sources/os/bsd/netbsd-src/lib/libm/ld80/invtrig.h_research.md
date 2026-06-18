# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/invtrig.h

This header declares ld80 inverse trig constants and inline polynomial evaluators.

It defines ld80-specific thresholds: linear asin/atan below `2^-32`, acos constant below `2^-65`, and atan constant above `2^65`. It supports an optional `STRUCT_DECLS` mode where constants are represented as a `LONGDOUBLE` struct instead of native long double.

The inline helpers `P()`, `Q()`, `T_even()`, and `T_odd()` evaluate the approximation polynomials when not in struct declaration mode.

It also remaps public-looking coefficient names to internal `_ItL_*` symbols.
