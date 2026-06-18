# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/runetype_local.h

Read completely: 145 lines.

This header defines the in-memory rune locale representation: `_RuneEntry`, `_RuneRange`, `_WCTransEntry`, `_WCTypeEntry`, indexes for standard classification/translation names, and `_RuneLocale` containing cached type/mapping arrays, extended ranges, variable data, Citrus ctype pointer, wctype/wctrans tables, and byte ctype tables.

Important interactions: central shared header for `rune.c`, `_wctype.c`, `_wctrans.c`, `iswctype_mb.c`, `multibyte.h`, and default rune table definitions.

Security/reliability notes: no executable code, but the structure layout is a private ABI within libc locale code. Range arrays must remain sorted for binary-search helpers.
