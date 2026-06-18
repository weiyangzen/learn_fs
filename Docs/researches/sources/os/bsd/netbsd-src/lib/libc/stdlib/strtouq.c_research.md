# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtouq.c

Instantiates the shared `_strtoul.h` unsigned parser for `u_quad_t`. It defines `_FUNCNAME` as `strtouq`, `__UINT` as `u_quad_t`, and `__UINT_MAX` as `UQUAD_MAX`.

All conversion semantics are inherited from the unsigned template.
