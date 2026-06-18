# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-9.c

Purpose: Generated Linux NLS module for ISO 8859-9 / Latin-5, described as Turkish.

Core structures and data:
- `charset2uni[256]` is close to Latin-1 but replaces selected positions with Turkish G/g breve, I dot/dotless, and S/s cedilla.
- Reverse mappings include `page00` and `page01`.
- Case tables include Turkish-specific byte case mappings.

Important behavior:
- `uni2char()` exact-maps supported Unicode values to one byte.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- Registers charset `"iso8859-9"`.

Dependencies and interfaces:
- Self-contained `nls_table` module.

Design notes and risks:
- Turkish-specific letters are sparse page 1 mappings, not custom code.
- Case tables are byte-oriented and not general Unicode locale-sensitive casing.
