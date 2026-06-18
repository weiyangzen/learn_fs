# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-5.c

Purpose: Generated Linux NLS module for ISO 8859-5, described as Cyrillic.

Core structures and data:
- `charset2uni[256]` maps byte range `0xa1` onward to Cyrillic and related symbols, including U+2116.
- Reverse maps include `page00`, `page04`, and `page21`.
- Case tables map Cyrillic uppercase/lowercase byte ranges and preserve nonletters.

Important behavior:
- `uni2char()` uses exact reverse lookup and emits one byte.
- `char2uni()` consumes one byte and rejects zero mappings.
- The registered charset name is `"iso8859-5"`.

Dependencies and interfaces:
- Standard generated NLS table module.

Design notes and risks:
- U+2116 maps through page 0x21 to byte `0xf0`.
- Cyrillic case folding is byte-table-based, not Unicode-general; it only covers characters representable in the charset.
