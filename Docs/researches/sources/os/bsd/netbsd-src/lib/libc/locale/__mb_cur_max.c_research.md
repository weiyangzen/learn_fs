# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/__mb_cur_max.c

Read completely: 41 lines.

This file defines two libc-wide multibyte length globals: `__mb_cur_max`, initialized to 1 for the C locale, and `__mb_len_max_runtime`, initialized to compile-time `MB_LEN_MAX`.

Important interactions: locale setup and multibyte conversion code use these values to expose or bound runtime multibyte lengths. `setlocale.c` resets `__mb_len_max_runtime` before locale changes.

Security/reliability notes: global mutable locale state can affect conversions process-wide. The file itself contains no logic.
