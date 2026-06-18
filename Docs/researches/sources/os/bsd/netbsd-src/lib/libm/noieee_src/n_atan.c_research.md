# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atan.c

Implements legacy `atan()` and `atanf()` as wrappers around `atan2(x, 1.0)`.

Key behavior:
- `atan()` calls `atan2(x, one)`.
- `atanf()` calls `atan2(x, one)` and casts to float.
- Weak aliases map `atan` and `atanf` to internal names.

Important dependencies: `namespace.h`, `mathimpl.h`, and `atan2()`.

Notable risks:
- Accuracy and special-case behavior are inherited entirely from `n_atan2.c`.
