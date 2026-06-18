# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llrintf.c

Macro instantiation wrapper for `llrintf(float)`, using `rintf()` and `long long`.

Key behavior: includes `s_lrint.c` after setting template macros.

Important dependencies: `s_lrint.c`, `rintf`, and fenv APIs.

Notable risks: template-based implementation hides function body in another source file.
