# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-9.c

Purpose: Generated Linux NLS module for ISO 8859-9 / Latin-5, described as Turkish.

Core structures and data:
- `charset2uni[256]` is close to ISO 8859-1 but replaces selected Icelandic positions with Turkish G/g breve, I dot/dotless, and S/s cedilla.
- Reverse mappings include `page00` and `page01`.
- Case tables include Turkish-specific byte case mappings such as dotted/dotless I behavior within the charset.

Important behavior:
- `uni2char()` exact-maps supported Unicode code points to one byte.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- The registered charset name is `"iso8859-9"`.

Dependencies and interfaces:
- Self-contained `nls_table` module.

Design notes and risks:
- The Turkish-specific letters are sparse page 1 mappings, not special-case code in the conversion functions.
- Case tables are byte-oriented and should not be assumed to implement locale-sensitive Unicode casing outside this charset.
