# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_monetary.c

Locale loader for `LC_MONETARY`.

Key behavior:
- Defines string fields for currency symbols, decimal/thousands separators, grouping, and signs.
- Defines char fields for fractional digits, symbol placement, spacing, and sign positions.
- Normal DB initialization reads string fields and 8-bit integer fields from Citrus DB.
- Fallback initialization reads line-oriented text, parses numeric char fields via `_bcs_strtol`, and validates range 0..127.
- Applies grouping fixups via `_CITRUS_FIXUP_CHAR_MAX_MD` or `__fix_locale_grouping_str`.
- Frees all allocated string fields on uninit or failure.
- Category DB path is `LC_MONETARY`; magic is `CtrsMO10`.

This loader populates NetBSD's `_MonetaryLocale`.
