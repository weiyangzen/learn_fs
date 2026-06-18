# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-1.c

Purpose: Generated Linux NLS module for ISO 8859-1 / Latin-1, described as Western European Languages.

Core structures and data:
- `charset2uni[256]` maps every byte value to the identical Unicode code point from U+0000 through U+00FF.
- `page00[256]` maps Unicode page 0 back to the identical byte values.
- `page_uni2charset[256]` only points page 0 at `page00`; all other pages are unmapped.
- `charset2lower[256]` and `charset2upper[256]` implement ASCII and Latin-1 case folding.

Important behavior:
- `uni2char()` rejects zero-length output buffers with `-ENAMETOOLONG`, looks up the Unicode high byte as a page selector, and emits exactly one byte for mapped nonzero entries.
- `char2uni()` maps one input byte through `charset2uni` and rejects byte `0x00` because the table value is `0x0000`.
- The module registers charset `"iso8859-1"` with both case tables.

Dependencies and interfaces:
- Standard `struct nls_table` implementation; no external NLS backend is loaded.
- Module init and exit are simple `register_nls()` / `unregister_nls()` wrappers.

Design notes and risks:
- The zero-entry-as-unmapped convention means NUL cannot be converted by `char2uni()` or `uni2char()` even though the mapping table contains it.
- Because Latin-1 is a direct byte-to-Unicode mapping for nonzero bytes, this file is mostly table data and is low in control-flow complexity.
