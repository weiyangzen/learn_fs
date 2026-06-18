# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llrint.c

Macro instantiation wrapper for `llrint(double)`. It defines `stype`, `roundit`, `dtype`, and `fn`, then includes `s_lrint.c`.

Key behavior: uses shared lrint template with `rint()` and `long long` result type.

Important dependencies: `s_lrint.c`, `rint`, and fenv handling in the template.

Notable risks: changes to `s_lrint.c` affect this function.
