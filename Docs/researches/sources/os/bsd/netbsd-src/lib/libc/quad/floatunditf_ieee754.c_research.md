# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatunditf_ieee754.c

Converts unsigned `u_quad_t` to `long double` using IEEE extended representation. It rejects VAX because VAX lacks a distinct long double format. The active implementation normalizes the 64-bit integer, fills `union ieee_ext_u` exponent and fraction fields, and returns `extu_ld`.

The file contains an inactive portable arithmetic version under `#if 0`. The active path supports optional middle fraction fields via `EXT_FRACHMBITS` and `EXT_FRACLMBITS`, adapting to platform extended-precision layouts.
