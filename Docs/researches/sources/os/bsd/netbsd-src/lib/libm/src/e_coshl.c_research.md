# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_coshl.c

Contains a long-double `coshl` implementation guarded by `__HAVE_LONG_DOUBLE`, plus a fallback.

Key behavior:
- If `__HAVE_LONG_DOUBLE` is not defined, `coshl` delegates to double `cosh`.
- Under `__HAVE_LONG_DOUBLE`, the file currently contains `#error SHOULD STOP HERE!!!` before the implementation, intentionally preventing that path from compiling.
- The disabled path includes long-double polynomial handling for `|x| < 1`, `k_hexpl`/`hexpl` for larger ranges, and overflow threshold handling.

Notable risk:
- Enabling `__HAVE_LONG_DOUBLE` for this file without addressing the explicit compile-time stop will break the build.
