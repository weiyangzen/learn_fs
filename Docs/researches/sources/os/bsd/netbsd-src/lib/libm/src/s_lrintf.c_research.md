# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lrintf.c

Macro instantiation wrapper for `lrintf(float)` using the shared `s_lrint.c` template.

Key behavior: sets `roundit` to `rintf` and `dtype` to `long`.

Important dependencies: `s_lrint.c` and `rintf`.

Notable risks: exception behavior is inherited from the template.
