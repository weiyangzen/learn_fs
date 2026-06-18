# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatdidf_ieee754.c

IEEE-754-specific signed `quad_t` to `double` conversion. It handles `0`, `1`, and `QUAD_MIN` specially, then uses `__builtin_clzll()` to normalize the integer, fills double fraction high/low fields, sets exponent bias, and returns the constructed double.

It directly creates the IEEE representation, avoiding intermediate floating arithmetic.
