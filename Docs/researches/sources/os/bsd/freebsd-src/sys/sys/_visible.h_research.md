# File Research: sources/os/bsd/freebsd-src/sys/sys/_visible.h

Header feature-test visibility policy.

Key elements:
- Normalizes old `_POSIX_C_SOURCE` values.
- Maps `_XOPEN_SOURCE`, `_POSIX_SOURCE`, `_POSIX_C_SOURCE`, `_ANSI_SOURCE`, `_C99_SOURCE`, `_C11_SOURCE`, `_C23_SOURCE`, and glibc-style ISO source macros to internal visibility macros.
- Defines `__POSIX_VISIBLE`, `__XSI_VISIBLE`, `__BSD_VISIBLE`, `__ISO_C_VISIBLE`, and `__EXT1_VISIBLE`.

Dependencies:
- Preprocessor feature-test macros.

Research notes:
- Controls which names public headers expose.
- Default environment exposes POSIX Issue 8, XSI 800, BSD extensions, C23, and Annex K extension visibility.
