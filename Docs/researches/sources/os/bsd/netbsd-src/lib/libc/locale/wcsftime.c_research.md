# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcsftime.c

Read completely: 116 lines.

This file implements `wcsftime` and `wcsftime_l`. It converts the wide format string to multibyte, calls `strftime_l`, then converts the result back to wide characters.

Important interactions: uses `wcstombs_l`, `strftime_l`, `mbstowcs_l`, `_current_locale()`, and `MB_CUR_MAX_L(loc)`.

Security/reliability notes: checks for multiplication overflow before allocating the multibyte output buffer. Stateful encodings are explicitly called out as a limitation because conversion state may be lost across format specifications.
