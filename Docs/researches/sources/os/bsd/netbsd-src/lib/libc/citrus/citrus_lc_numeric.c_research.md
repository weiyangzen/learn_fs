# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_numeric.c

Locale loader for `LC_NUMERIC`.

Key behavior:
- Loads `decimal_point`, `thousands_sep`, and `grouping`.
- Normal path reads strings from a Citrus DB.
- Fallback path reads three lines from a memory stream.
- Applies grouping conversion through `_CITRUS_FIXUP_CHAR_MAX_MD` or `__fix_locale_grouping_str`.
- Frees all allocated fields on uninit/failure.
- Category DB path is `LC_NUMERIC`; magic is `CtrsNU10`.

This loader populates NetBSD's `_NumericLocale`.
