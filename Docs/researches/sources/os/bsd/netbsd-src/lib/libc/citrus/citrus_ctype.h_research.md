# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype.h

Inline API wrapper around a `_citrus_ctype_rec` dispatch table.

Key behavior:
- Declares open/close and the external `_citrus_ctype_default`.
- Provides inline wrappers for multibyte and wide-character operations: `mblen`, `mbrlen`, `mbrtowc`, `mbsrtowcs`, `mbsnrtowcs`, `mbstowcs`, `mbtowc`, `wcrtomb`, `wcsrtombs`, `wcsnrtombs`, `wcstombs`, `wctomb`, `btowc`, and `wctob`.
- Asserts required ops before dispatch.

Notable detail:
- `mbsnrtowcs` and `wcsnrtombs` pass the ctype record itself, not only closure, matching the v3 ABI/fallback shape.
