# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatdisf_ieee754.c

IEEE-754-specific signed `quad_t` to `float` conversion. It handles zero, one, and `QUAD_MIN`, then normalizes the magnitude and fills an IEEE single union.

On LP64 or MIPS n32 it uses `__builtin_clzll()`. On 32-bit paths it inspects the high and low halves manually to compute the leading-zero count and fraction. It does not implement explicit rounding beyond truncating fraction bits into the target representation.
