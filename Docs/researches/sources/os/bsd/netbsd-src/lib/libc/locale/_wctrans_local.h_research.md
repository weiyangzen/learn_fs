# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wctrans_local.h

Read completely: 60 lines.

This header declares `_towctrans_ext` and defines inline helpers for wide-character translation. `_towctrans_priv` uses the cached translation table for small runes and falls back to `_towctrans_ext`; `_wctrans_lower` and `_wctrans_upper` return the locale's lower/upper translation entries.

Important interactions: used by `_wctype.c`, `iswctype_mb.c`, and `rune.c` to share translation lookup logic.

Security/reliability notes: relies on diagnostic assertions that translation entries are initialized. No standalone runtime behavior beyond inline table access.
