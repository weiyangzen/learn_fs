# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstold.c

Read completely: 51 lines.

This file instantiates `_wcstod.h` for `wcstold` and `wcstold_l`, with return type `long double` and backend `strtold_l`.

Important interactions: provides weak aliases and reuses the floating wide-string conversion template.

Security/reliability notes: inherits template limitations around multibyte conversion and end-pointer mapping.
