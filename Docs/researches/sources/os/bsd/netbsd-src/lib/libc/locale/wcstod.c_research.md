# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstod.c

Read completely: 51 lines.

This file instantiates `_wcstod.h` for `wcstod` and `wcstod_l`, with return type `double` and backend `strtod_l`.

Important interactions: provides weak aliases and includes the shared floating conversion template.

Security/reliability notes: inherits the template's multibyte conversion behavior and end-pointer limitations.
