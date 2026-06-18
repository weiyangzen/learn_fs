# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wctype.c

Read completely: 112 lines.

This file implements rune type lookup. `_runetype_priv` returns cached classification bits for small runes or binary-searches extended ranges for larger runes, supporting either per-rune type arrays or a uniform range map. `_iswctype_priv` masks the resulting bits with a `_WCTypeEntry`.

Important interactions: all `isw*` and width functions in `iswctype_mb.c` depend on these helpers. `rune.c` uses `_runetype_priv` while building byte-oriented ctype compatibility tables.

Security/reliability notes: assumes sorted and valid `_RuneRange` data loaded from locale files or default tables. Returns zero for `WEOF` and unknown ranges.
