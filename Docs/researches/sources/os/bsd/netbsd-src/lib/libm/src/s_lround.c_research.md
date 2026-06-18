# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lround.c

Template implementation for `lround`-family functions. Default instantiation is `lround(double)`.

Key behavior: checks range against type limits adjusted by 0.5, rounds away from zero via `roundit`, casts to integer, and raises `FE_INVALID` returning `DTYPE_MAX` when out of range.

Important dependencies: `limits.h`, `fenv.h`, `math.h`, and template macros.

Notable risks: compile-time `INRANGE` logic depends on source/destination precision relationships.
