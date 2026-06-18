# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-1.c

Purpose: Generated Linux NLS module for ISO 8859-1 / Latin-1, described as Western European Languages.

Core structures and data:
- `charset2uni[256]` maps byte values directly to Unicode U+0000 through U+00FF.
- `page00[256]` maps Unicode page 0 back to byte values.
- `page_uni2charset[256]` only maps page 0; all other pages are unmapped.
- `charset2lower` and `charset2upper` implement ASCII and Latin-1 byte-level casing.

Important behavior:
- `uni2char()` does a page-based reverse lookup and emits one byte.
- `char2uni()` maps one byte through `charset2uni`.
- Both paths treat `0x0000`/`0x00` as an unmapped sentinel, so NUL is rejected by the common generated logic.

Dependencies and interfaces:
- Self-contained `struct nls_table` implementation.
- Module lifecycle is `register_nls()` / `unregister_nls()` for charset `"iso8859-1"`.

Design notes and risks:
- Low control-flow complexity; behavior is almost entirely table-driven.
- Exact mapping only: no normalization, transliteration, or fallback substitution.
