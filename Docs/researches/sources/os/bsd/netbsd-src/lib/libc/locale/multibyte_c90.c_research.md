# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte_c90.c

Read completely: 167 lines.

This file implements legacy C90 multibyte APIs and `wcsnrtombs`: `mblen`, `mbstowcs`, `mbtowc`, `wcstombs`, `wcsnrtombs`, and `wctomb`, with locale-aware variants.

Important interactions: non-restartable APIs call the locale's Citrus ctype directly. `wcsnrtombs_l` uses the restartable state helpers from `multibyte.h`.

Security/reliability notes: errors are surfaced through `errno` from Citrus. As with other wrappers, behavior relies on the ctype backend honoring libc conversion contracts.
