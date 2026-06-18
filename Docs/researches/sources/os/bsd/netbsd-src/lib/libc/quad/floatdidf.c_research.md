# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatdidf.c

Generic signed `quad_t` to `double` conversion via `__floatdidf()`. It records sign, converts the magnitude to a `union uu`, computes `high * 2^32 + low` in double, and reapplies the sign.

This is portable code that does not inspect floating-point representation, but it may be less efficient than architecture-specific or IEEE-aware implementations.
