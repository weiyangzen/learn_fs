# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/global_locale.c

Read completely: 202 lines.

This file defines default C-locale category data, the shared `_C_cache`, the mutable global locale `_lc_global_locale`, and immutable `_lc_C_locale`. Defaults cover messages, monetary, numeric, time, rune/ctype, and `struct lconv` cache fields.

Important interactions: `_current_locale()` returns `_lc_global_locale`; `newlocale`, `setlocale`, `localeconv`, `nl_langinfo`, and category templates all rely on these baseline objects. The C cache also points at system error-list storage for locale-sensitive error message support.

Security/reliability notes: most fields point to static string literals or default locale objects. `_lc_global_locale` is mutable process-wide state and is not inherently synchronized.
