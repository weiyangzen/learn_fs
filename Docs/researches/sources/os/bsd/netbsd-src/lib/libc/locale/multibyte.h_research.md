# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte.h

Read completely: 132 lines.

This header defines the private layout used to store `_RuneLocale *` and Citrus ctype state inside `mbstate_t`. It provides helpers to reinterpret `mbstate_t` as `_RuneState`, extract the rune locale, ctype object, and private state, initialize state, and lazily fix up state for a locale.

Important interactions: `multibyte_amd1.c` and `multibyte_c90.c` use these helpers for restartable and legacy multibyte APIs. The `_PRIVSIZE` value is passed to Citrus ctype open in `rune.c`.

Security/reliability notes: correctness depends on `mbstate_t` being large and aligned enough for the private state. `_fixup_ps` initializes state when the stored runelocale is NULL or forced.
