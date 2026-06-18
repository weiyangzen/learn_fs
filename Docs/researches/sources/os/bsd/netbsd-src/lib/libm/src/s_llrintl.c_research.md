# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llrintl.c

Macro instantiation wrapper for `llrintl(long double)` when long double exists; otherwise falls back to `llrint()`.

Key behavior: includes `s_lrint.c` with `rintl()` and `long long` result type.

Important dependencies: `s_lrint.c`, `rintl`, and `llrint`.

Notable risks: fallback narrows long double to double.
