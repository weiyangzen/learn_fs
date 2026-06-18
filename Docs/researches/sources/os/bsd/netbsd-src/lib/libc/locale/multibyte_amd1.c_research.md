# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte_amd1.c

Read completely: 258 lines.

This file implements restartable C95/C99-style multibyte APIs and related helpers: `mbrlen`, `mbsinit`, `mbrtowc`, `mbsrtowcs`, `mbsnrtowcs`, `wcrtomb`, `wcsrtombs`, `btowc`, `wctob`, and `_mb_cur_max_l`, with locale-aware `_l` variants.

Important interactions: wrappers mostly call Citrus ctype methods after `_fixup_ps` ensures `mbstate_t` is bound to the active rune locale. Byte/wide single-character conversion uses the locale's `rl_citrus_ctype` directly.

Security/reliability notes: Citrus errors are copied to `errno`, but return values come from the backend. State lifetime and locale binding depend on callers not reusing `mbstate_t` across incompatible locales without reset.
